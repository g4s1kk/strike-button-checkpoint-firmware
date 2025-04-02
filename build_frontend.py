import flet as ft
import json
import websockets

import src.webconf as webconf


WS_ADDR = f"ws://{webconf.BACKEND_IP_ADDR}:{webconf.WEB_PORT}/ws"
LOG_DOWNLOAD_ADDR = f"http://{webconf.BACKEND_IP_ADDR}:{webconf.WEB_PORT}/{webconf.WEB_DOWNLOAD_LOG_ENDPOINT}"


def main(page: ft.Page):
    page.title = "Admin Panel"
    page.vertical_alignment = "center"
    
    # Состояние (ответы от бэка)
    output_bar = ft.Text("Здесь будет отчёт...", selectable=True)
    status_bar = ft.Text()
    
    # 1. Кнопка "Просмотр отчёта" (запрос по WS)
    async def view_report(e):
        async with websockets.connect(WS_ADDR) as ws:
            await ws.send(json.dumps({"action": "get_report"}))
            response = await ws.recv()
            output_bar.value = response
            page.update()
    
    # 2. Кнопка "Скачать лог" (обычный HTTP-запрос)
    async def download_log(e):
        page.launch_url(LOG_DOWNLOAD_ADDR)
    
    # 3. Кнопка "Загрузить конфиг" (отправка файла)
    async def upload_config(e):
        file_picker = ft.FilePicker()
        page.overlay.append(file_picker)
        await file_picker.pick_files()
        
        if file_picker.result:
            file = file_picker.result.files[0]
            content = await file.read_as_text()
            async with websockets.connect(WS_ADDR) as ws:
                await ws.send(json.dumps({
                    "action": "upload_config",
                    "name": file.name,
                    "content": content
                }))
                response = await ws.recv()
                status_bar.value = response
                page.update()

    async def start_game(e):
        async with websockets.connect(WS_ADDR) as ws:
            await ws.send(json.dumps({"action": "start_game"}))
            response = await ws.recv()
            status_bar.value = response
            page.update()

    async def get_status(e):
        async with websockets.connect(WS_ADDR) as ws:
            await ws.send(json.dumps({"action": "get_status"}))
            response = await ws.recv()
            output_bar.value = response
            page.update()

    async def reboot(e):
        async with websockets.connect(WS_ADDR) as ws:
            await ws.send(json.dumps({"action": "reboot"}))
            response = await ws.recv()
            status_bar.value = response
            page.update()
    
    # Интерфейс
    page.add(
        ft.Column([
            ft.ElevatedButton("Просмотр отчёта", on_click=view_report),
            ft.ElevatedButton("Скачать лог", on_click=download_log),
            ft.ElevatedButton("Загрузить конфиг", on_click=upload_config),
            ft.ElevatedButton("Старт игры", on_click=start_game),
            ft.ElevatedButton("Статус чекпойнта", on_click=get_status),
            ft.ElevatedButton("Перезагрузка устройства", on_click=reboot),
            output_bar,
            status_bar
        ])
    )

# Собираем фронт в HTML (для Microdot)
ft.app(target=main, view=None)
