from configs.ApplicationConfig import ApplicationConfig
from context import Context
from transport.sanic import endpoints


def get_routes(config: ApplicationConfig, context: Context) -> tuple:
    return (
        endpoints.HealthEndpoint(
            config=config, context=context, uri='/', methods=['GET', 'POST']
        ),
        endpoints.GalleryEndpoint(
            config=config, context=context, uri='/gallery', methods=['GET']
        ),
        endpoints.FilesEndpoint(
            config=config, context=context, uri='/files/<file_id:int>', methods=['GET']
            # auth_required=True
        ),
        endpoints.FilesEndpoint(
            config=config, context=context, uri='/files', methods=['POST'],
            auth_required=True
        ),
        endpoints.GetFileEndpoint(
            config=config, context=context, uri='/file', methods=['GET', 'POST']
        ),
        endpoints.GetYoutubeFileEndpoint(
            config=config, context=context, uri='/youtube_file', methods=['GET', 'POST']
        ),
        endpoints.GetProgressEndpoint(
            config=config, context=context, uri='/progress/<progress_id:int>', methods=['GET', 'POST']
        ),
        endpoints.GetListVideosEndpoint(
            config=config, context=context, uri='/list_videos', methods=['GET']
        ),
    )
