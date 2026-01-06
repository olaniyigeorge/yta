# from fastapi import FastAPI
# import uvicorn

# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
# from fastapi import Request
# from dotenv import load_dotenv
# from contextlib import asynccontextmanager

# load_dotenv()

# from config import AppConfig

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """ TODO: investigate impact on performance
#         Manages the lifespan of the yta-api App. It
#         initializes the database manager which manages 
#         data on server wake up and cleanly closes it on
#         shutdown
#     """
#     try:
#         # # Initialize database
#         # engine_kwargs = {}
#         # if "sqlite" in AppConfig.DATABASE_URL:
#         #     engine_kwargs.update(
#         #         {
#         #             "connect_args": {"check_same_thread": False},
#         #             "poolclass": sqlalchemy.StaticPool,
#         #         }
#         #     )

#         # db_manager.initialize(AppConfig.DATABASE_URL, **engine_kwargs)

#         # # Create tables 
#         # await db_manager.create_tables()
        

#         # logger.info("Application startup complete")
#         yield
#     except Exception as e:
#         logger.error(f"Startup failed: {e}")
#         raise
#     finally:
#         # Shutdown
#         # await db_manager.close()
#         logger.info("Application shutdown complete")


# app = FastAPI(title=AppConfig.PROJECT_NAME, docs_url="/api/docs", lifespan=lifespan)


# # mount static files dir
# templates = Jinja2Templates(directory="src/templates")
# app.mount("/static", StaticFiles(directory="src/static"), name="static")


# # app.include_router(auth_router)

# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     base_url = AppConfig.DOMAIN
#     # TODO : Version documentation

#     return templates.TemplateResponse(
#         request,
#         "index.html",
#         {
#             "name": "Youtube Automation",
#             "details": "Full stack Youtube Automation System ",
#             "docs": f"api/docs",
#         },
#     )



# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app", 
#         host="0.0.0.0", 
#         reload=True, 
#         port=8000
#     )

