import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import json
import os
from datetime import datetime
from plyer import notification
import threading
import time

# File to store tasks
TASKS_FILE = "tasks.json"

# Load tasks from file
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as file:
            return json.load(file)
    return {"folders": {"Default": []}}

# Save tasks to file
def save_tasks():
    with open(TASKS_FILE, 'w') as file:
        json.dump(tasks, file, indent=4)

# Add a task
def add_task(event=None):
    task = entry_task.get().strip()
    due_date = cal_due_date.get_date() if cal_due_date.get_date() else None
    folder = folder_var.get()
    if task:
        task_data = {
            "task": task,
            "completed": False,
            "due_date": due_date,
            "reminder": None,
            "folder": folder
        }
        tasks["folders"][folder].append(task_data)
        update_task_list(folder)
        entry_task.delete(0, tk.END)
        save_tasks()
    else:
        messagebox.showwarning("Warning", "Please enter a task.")

# Update task list based on selected folder
def update_task_list(folder):
    listbox_tasks.delete(0, tk.END)
    for task in tasks["folders"][folder]:
        task_text = task["task"]
        if task["due_date"]:
            task_text += f" (Due: {task['due_date']})"
        listbox_tasks.insert(tk.END, task_text)
        if task["completed"]:
            listbox_tasks.itemconfig(tk.END, {'bg': 'light green'})

# Delete a task
def delete_task():
    try:
        folder = folder_var.get()
        task_index = listbox_tasks.curselection()[0]
        task_text = listbox_tasks.get(task_index)
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete '{task_text}'?")
        if confirm:
            tasks["folders"][folder].pop(task_index)
            update_task_list(folder)
            save_tasks()
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to delete.")

# Toggle task completion
def toggle_completion():
    try:
        folder = folder_var.get()
        task_index = listbox_tasks.curselection()[0]
        task = tasks["folders"][folder][task_index]
        task["completed"] = not task["completed"]
        listbox_tasks.itemconfig(task_index, {'bg': 'light green' if task["completed"] else 'white'})
        save_tasks()
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to mark as completed.")

# Set a reminder for a task
def set_reminder():
    try:
        folder = folder_var.get()
        task_index = listbox_tasks.curselection()[0]
        task = tasks["folders"][folder][task_index]
        reminder_time = entry_reminder.get().strip()
        if reminder_time:
            task["reminder"] = reminder_time
            threading.Thread(target=schedule_reminder, args=(task,)).start()
            messagebox.showinfo("Reminder Set", f"Reminder set for {reminder_time}")
            save_tasks()
        else:
            messagebox.showwarning("Warning", "Please enter a reminder time.")
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to set a reminder.")

# Schedule a reminder
def schedule_reminder(task):
    reminder_time = datetime.strptime(task["reminder"], "%Y-%m-%d %H:%M")
    while datetime.now() < reminder_time:
        time.sleep(1)
    notification.notify(
        title="Task Reminder",
        message=f"Don't forget: {task['task']}",
        timeout=10
    )

# Create a new folder
def create_folder():
    folder_name = entry_folder.get().strip()
    if folder_name:
        if folder_name not in tasks["folders"]:
            tasks["folders"][folder_name] = []
            folder_menu["menu"].add_command(label=folder_name, command=lambda f=folder_name: select_folder(f))
            entry_folder.delete(0, tk.END)
            save_tasks()
        else:
            messagebox.showwarning("Warning", "Folder already exists.")
    else:
        messagebox.showwarning("Warning", "Please enter a folder name.")

# Select a folder
def select_folder(folder):
    folder_var.set(folder)
    update_task_list(folder)

# Initialize tasks
tasks = load_tasks()

# Create the main window
root = tk.Tk()
root.title("Advanced To-Do List")
root.geometry("700x500")
root.resizable(False, False)

# Style configuration
style = ttk.Style()
style.configure("TButton", padding=5, font=("Helvetica", 10))
style.configure("TEntry", padding=5, font=("Helvetica", 12))

# Tabbed interface
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Task Management Tab
tab_tasks = ttk.Frame(notebook)
notebook.add(tab_tasks, text="Tasks")

# Folder Management Tab
tab_folders = ttk.Frame(notebook)
notebook.add(tab_folders, text="Folders")

# Task Management Tab Content
frame_entry = ttk.Frame(tab_tasks)
frame_entry.pack(pady=10, padx=10, fill=tk.X)

entry_task = ttk.Entry(frame_entry, width=40, font=("Helvetica", 12))
entry_task.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
entry_task.bind("<Return>", add_task)

button_add = ttk.Button(frame_entry, text="Add Task", command=add_task)
button_add.pack(side=tk.LEFT)

# Due Date Calendar
frame_due_date = ttk.Frame(tab_tasks)
frame_due_date.pack(pady=10, padx=10, fill=tk.X)

cal_due_date = Calendar(frame_due_date, selectmode="day", date_pattern="yyyy-mm-dd")
cal_due_date.pack(side=tk.LEFT, padx=5)

# Reminder Entry
frame_reminder = ttk.Frame(tab_tasks)
frame_reminder.pack(pady=10, padx=10, fill=tk.X)

label_reminder = ttk.Label(frame_reminder, text="Set Reminder (YYYY-MM-DD HH:MM):")
label_reminder.pack(side=tk.LEFT, padx=5)

entry_reminder = ttk.Entry(frame_reminder, width=20, font=("Helvetica", 12))
entry_reminder.pack(side=tk.LEFT, padx=5)

button_reminder = ttk.Button(frame_reminder, text="Set Reminder", command=set_reminder)
button_reminder.pack(side=tk.LEFT)

# Task List
frame_tasks = ttk.Frame(tab_tasks)
frame_tasks.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

listbox_tasks = tk.Listbox(frame_tasks, width=50, height=15, font=("Helvetica", 12), selectbackground="#a6a6a6")
listbox_tasks.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar_tasks = ttk.Scrollbar(frame_tasks, orient=tk.VERTICAL, command=listbox_tasks.yview)
scrollbar_tasks.pack(side=tk.RIGHT, fill=tk.Y)

listbox_tasks.config(yscrollcommand=scrollbar_tasks.set)

# Buttons for Task Actions
frame_buttons = ttk.Frame(tab_tasks)
frame_buttons.pack(pady=10, padx=10, fill=tk.X)

button_delete = ttk.Button(frame_buttons, text="Delete Task", command=delete_task)
button_delete.pack(side=tk.LEFT, padx=5)

button_complete = ttk.Button(frame_buttons, text="Toggle Completion", command=toggle_completion)
button_complete.pack(side=tk.LEFT, padx=5)

# Folder Management Tab Content
frame_folder_entry = ttk.Frame(tab_folders)
frame_folder_entry.pack(pady=10, padx=10, fill=tk.X)

entry_folder = ttk.Entry(frame_folder_entry, width=30, font=("Helvetica", 12))
entry_folder.pack(side=tk.LEFT, padx=5)

button_create_folder = ttk.Button(frame_folder_entry, text="Create Folder", command=create_folder)
button_create_folder.pack(side=tk.LEFT)

# Folder Selection
frame_folder_select = ttk.Frame(tab_folders)
frame_folder_select.pack(pady=10, padx=10, fill=tk.X)

folder_var = tk.StringVar(value="Default")
folder_menu = ttk.OptionMenu(frame_folder_select, folder_var, "Default", *tasks["folders"].keys(), command=lambda f: select_folder(f))
folder_menu.pack(side=tk.LEFT, padx=5)

# Load tasks into the listbox
update_task_list("Default")

# Start the main loop
root.mainloop()