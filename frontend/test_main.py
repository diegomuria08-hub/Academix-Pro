import traceback
import flet as ft
from app.main import main

try:
    page = ft.Page(None, 'ses')
    page.route = '/login'
    main(page)
    print("SUCCESS")
except Exception as e:
    traceback.print_exc()
