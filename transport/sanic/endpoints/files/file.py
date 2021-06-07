import os
import uuid

import youtube_dl
from sanic import response
from sanic.request import Request
from sanic.response import BaseHTTPResponse, file
import hashlib

from db.database import DBSession
from db.exceptions import DBDataException, DBIntegrityException, DBFileNotExistsException
from db.queries.progress import get_progress_percantage, update_progress, create_progress
from db.queries.videos_queue import add_video_in_queue, get_list_videos, check_existing_hash, \
    get_num_violathions_by_videoid
from transport.sanic.endpoints import BaseEndpoint
from db.queries import file as file_queries
from transport.sanic.exceptions import SanicDBException, SanicFileNotFound, SanicUserConflictException


class FilesEndpoint(BaseEndpoint):

    async def method_get(
            self, request: Request, body: dict, session: DBSession, file_id: int = None, *args, **kwargs
    ) -> BaseHTTPResponse:
        try:
            file = file_queries.get_file_by_id(session, file_id=file_id)
        except DBFileNotExistsException:
            raise SanicFileNotFound('File not found')
        if file.sender_id != body['uid']:
            if body['uid'] not in file_queries.get_recipients_by_file_id(session, file_id):
                raise SanicUserConflictException("You don't have access to the file")

        return await response.file(os.path.join('raw_files', file.ref_file), status=200)

    async def method_post(
            self, request: Request, body: dict, session: DBSession, *args, **kwargs
    ) -> BaseHTTPResponse:
        if not os.path.exists('raw_files'):
            os.makedirs('raw_files')
        files = request.files['file']
        file_names = []
        for f in files:
            filename = '.'.join([str(uuid.uuid4()), f.name.split('.')[-1]])
            path_to_file = os.path.join('raw_files', filename)
            with open(path_to_file, 'wb') as file:
                file.write(f.body)
            file_names.append(filename)
        files = []
        for f_name in file_names:
            file = file_queries.create_file(session, body['uid'], f_name)
            files.append(file)
        try:
            session.commit_session()
        except (DBDataException, DBIntegrityException) as e:
            raise SanicDBException(str(e))
        file_ids = []
        for file in files:
            file_ids.append(file.id)

        return await self.make_response_json(body={"file_ids": file_ids}, status=201)


class GetFileEndpoint(BaseEndpoint):
    async def method_get(
            self, request: Request, body: dict, session: DBSession, *args, **kwargs
    ) -> BaseHTTPResponse:

        return await file('raw_files/cut_final_10sek_v2_final_with_crossing.mp4')

    async def method_post(
            self, request: Request, body: dict, session: DBSession, *args, **kwargs
    ) -> BaseHTTPResponse:
        if not os.path.exists('raw_files'):
            os.makedirs('raw_files')
        files = request.files['file']
        file_names = []
        for f in files:
            filename = '.'.join([str(uuid.uuid4()), f.name.split('.')[-1]])
            path_to_file = os.path.join('raw_files', filename)
            with open(path_to_file, 'wb') as file:
                file.write(f.body)
            file_names.append(filename)
        print(file_names)

        with open(os.path.join(*['raw_files', file_names[0]]), "rb") as f:
            file_hash = hashlib.md5()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
        hash_video = file_hash.hexdigest()
        if check_existing_hash(session, hash_video):
            return await self.make_response_json(body={"existing": 1, "file_name": file_names[0]}, status=201)
        queue_id = add_video_in_queue(session, file_names[0], hash_video)
        progress_id = create_progress(session, queue_id)
        return await self.make_response_json(body={"progress_id": progress_id, "file_name": file_names[0]}, status=201)


class GetYoutubeFileEndpoint(BaseEndpoint):

    async def method_post(
            self, request: Request, body: dict, session: DBSession, *args, **kwargs
    ) -> BaseHTTPResponse:
        if not os.path.exists('raw_files'):
            os.makedirs('raw_files')
        youtube_link = request.json['file']
        print(youtube_link)
        filename = str(uuid.uuid4())
        path_to_file = os.path.join('raw_files', filename)
        print(path_to_file)
        ydl_opts = {
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'outtmpl': path_to_file
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_link])
        file_names = []
        # filename = '.'.join([str(uuid.uuid4()), f.name.split('.')[-1]])
        # path_to_file = os.path.join('raw_files', filename)
        file_names.append(filename + '.mp4')
        print(file_names)

        with open(os.path.join(*['raw_files', file_names[0]]), "rb") as f:
            file_hash = hashlib.md5()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
        hash_video = file_hash.hexdigest()
        if check_existing_hash(session, hash_video):
            return await self.make_response_json(body={"existing": 1, "file_name": file_names[0]}, status=201)
        queue_id = add_video_in_queue(session, file_names[0], hash_video)
        progress_id = create_progress(session, queue_id)
        return await self.make_response_json(body={"progress_id": progress_id, "file_name": file_names[0]}, status=201)

class GetProgressEndpoint(BaseEndpoint):
    async def method_get(
            self, request: Request, body: dict, session: DBSession, progress_id: int = None, *args, **kwargs
    ) -> BaseHTTPResponse:
        progress_ptg = get_progress_percantage(session, progress_id)
        session.close_session()
        print(progress_ptg)
        return await self.make_response_json(body={"progress_percantage": progress_ptg}, status=201)

    async def method_post(
            self, request: Request, body: dict, session: DBSession, progress_id: int = None, *args, **kwargs
    ) -> BaseHTTPResponse:
        # file_name = request.json['file_name']
        # await predict_video.predict_video_outside(
        #     os.path.join('raw_files', file_name),
        #     os.path.join(*['web', 'static', 'raw', file_name[:-4] + '2.mp4']),
        #     session,
        #     progress_id
        # )

        return await self.make_response_json(status=201)


class GetListVideosEndpoint(BaseEndpoint):
    async def method_get(
            self, request: Request, body: dict, session: DBSession, progress_id: int = None, *args, **kwargs
    ) -> BaseHTTPResponse:
        videos = get_list_videos(session)
        videos_name = []
        num_violations = []
        for video in videos:
            videos_name.append(video.video_name)
            num_violations.append(get_num_violathions_by_videoid(session, video.id))
        print(videos_name, num_violations)
        return await self.make_response_json(body={"videos": videos_name, "num_violations": num_violations}, status=201)
