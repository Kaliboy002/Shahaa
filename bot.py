from gradio_client import Client, file

client = Client("felixrosberg/face-swap")

client.predict(
  target=file('https://felixrosberg-face-swap.hf.space/file=/tmp/gradio/aef8d7903315ce4b50bb1c347f261c889b4ebced/IMG_20250121_074544_288.jpg'),
  source=file('https://felixrosberg-face-swap.hf.space/file=/tmp/gradio/746368040a104693461895e19d6527df3625815f/file_0.jpg'),
  slider=100,
  adv_slider=100,
  settings=[],
  api_name="/run_inference"
)
