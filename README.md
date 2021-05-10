# detecting-traffic-violations-app
### Install
`git clone --recurse-submodules https://github.com/DmitryCS/detecting-traffic-violations-app3.git`
<br><br>
`pip install -r requirements.txt`

`pip install -r ./sort/requirements.txt`

`python -m pip install -e detectron2`

Add weights to `output/model_final.pth`
Сustomize the database PostgreSQL using `init.sql`

### Run
`python main_predict_video.py`
`python main_sanic.py`
