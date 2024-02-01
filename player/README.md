# edp-vmemo-subclip

## 起動方法

```sh
pip install poetry
cd ./player
poetry install
poetry run python main.py
```

## `.env`

- `VMEMO_MOVIE_DIR` : 再生する動画のディレクトリパス

- `VMEMO_OUTPUT_DIR` : 切り抜き動画を保存するパス

- `VMEMO_CLIP_DURATION` : 切り抜き動画の長さ(秒)

- `VMEMO_DISPLAY` : 表示するディスプレイの番号

- `VMEMO_SERIAL_PORT` : リモコン受信機のシリアルポート
