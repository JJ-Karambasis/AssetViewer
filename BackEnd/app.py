from flask import Flask
from renderer.vk.instance import init_vulkan

def create_app():
    app = Flask(__name__)

    vk = init_vulkan()
    if vk is None:
        return "Vulkan has failed to initialize"

    @app.route("/hello")
    def home():
        return "hello", 200
    
    return app

app = create_app()
