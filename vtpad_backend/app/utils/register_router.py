from fastapi import FastAPI


def register_router(router_list: list, application: FastAPI, global_prefix: str = ''):
    for i in router_list:
        application.include_router(i, prefix=global_prefix)
