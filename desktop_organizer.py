import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# 文件分类配置
CATEGORIES = {
    "Word文档": [".docx", ".doc"],
    "Excel表格": [".xlsx", ".xls", ".csv"],
    "演示PPT": [".pptx", ".ppt"],
    "PDF文件": [".pdf"],
    "文本笔记": [".txt", ".md", ".rtf"],
    "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
    "视频": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
    "音频": [".mp3", ".wav", ".flac", ".aac"],
    "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "程序安装": [".exe", ".msi", ".dmg", ".apk"],
    "代码脚本": [".py", ".js", ".html", ".css", ".java"],
    "配置文件": [".json", ".xml", ".yaml", ".ini"],
}


class DesktopOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("桌面整理器 - 按文件类型分类")
        self.root.geometry("600x500")

        # 变量
        self.folder_path = tk.StringVar(value=str(Path.home() / "Desktop"))
        self.check_vars = {}

        self.setup_ui()

    def setup_ui(self):
        # 标题
        title_label = tk.Label(self.root, text="桌面/文件夹整理器", font=("微软雅黑", 16, "bold"))
        title_label.pack(pady=10)

        # 路径选择区域
        path_frame = tk.Frame(self.root)
        path_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(path_frame, text="目标文件夹:").pack(side="left")
        path_entry = tk.Entry(path_frame, textvariable=self.folder_path, width=40)
        path_entry.pack(side="left", padx=5)

        tk.Button(path_frame, text="浏览...", command=self.browse_folder).pack(side="left")

        # 说明文字
        info_label = tk.Label(self.root, text="请勾选要整理的文件类型（勾选的类型会被移动到对应子文件夹）",
                              fg="gray", font=("微软雅黑", 9))
        info_label.pack(pady=5)

        # 创建复选框区域（带滚动条）
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=10)

        canvas = tk.Canvas(canvas_frame)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 全选/全不选按钮
        select_frame = tk.Frame(scrollable_frame)
        select_frame.pack(fill="x", pady=5)
        tk.Button(select_frame, text="全选", command=self.select_all, width=8).pack(side="left", padx=5)
        tk.Button(select_frame, text="全不选", command=self.select_none, width=8).pack(side="left", padx=5)
        tk.Button(select_frame, text="推荐配置", command=self.recommend, width=8).pack(side="left", padx=5)

        # 创建复选框（每行2个）
        row_frame = None
        for i, (category, exts) in enumerate(CATEGORIES.items()):
            if i % 2 == 0:
                row_frame = tk.Frame(scrollable_frame)
                row_frame.pack(fill="x", pady=2)

            var = tk.BooleanVar(value=True)  # 默认全选
            self.check_vars[category] = var
            cb = tk.Checkbutton(row_frame, text=f"{category} ({len(exts)}种格式)",
                                variable=var, anchor="w", width=25)
            cb.pack(side="left", padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 整理按钮和进度区域
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        self.organize_btn = tk.Button(btn_frame, text="开始整理", command=self.organize,
                                      bg="#4CAF50", fg="white", font=("微软雅黑", 12),
                                      width=15, height=1)
        self.organize_btn.pack()

        # 结果显示区域
        self.result_text = tk.Text(self.root, height=8, width=70, font=("Consolas", 9))
        self.result_text.pack(pady=10, padx=20, fill="both")

        # 滚动条
        scroll_text = tk.Scrollbar(self.result_text)
        scroll_text.pack(side="right", fill="y")
        self.result_text.config(yscrollcommand=scroll_text.set)
        scroll_text.config(command=self.result_text.yview)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def select_all(self):
        for var in self.check_vars.values():
            var.set(True)

    def select_none(self):
        for var in self.check_vars.values():
            var.set(False)

    def recommend(self):
        """推荐配置：常用文档类全选，其他按需"""
        recommend_list = ["Word文档", "Excel表格", "演示PPT", "PDF文件", "文本笔记", "图片", "压缩包"]
        for cat, var in self.check_vars.items():
            var.set(cat in recommend_list)

    def organize(self):
        """执行整理操作"""
        folder = Path(self.folder_path.get())

        if not folder.exists():
            messagebox.showerror("错误", f"文件夹不存在:\n{folder}")
            return

        # 获取勾选的类型
        selected_categories = [cat for cat, var in self.check_vars.items() if var.get()]

        if not selected_categories:
            messagebox.showwarning("提示", "请至少选择一种文件类型")
            return

        # 清空结果显示
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"整理目标: {folder}\n")
        self.result_text.insert(tk.END, f"整理类型: {', '.join(selected_categories)}\n")
        self.result_text.insert(tk.END, "=" * 50 + "\n\n")

        # 禁用按钮
        self.organize_btn.config(state="disabled", text="整理中...")
        self.root.update()

        moved_count = 0
        error_count = 0

        try:
            # 遍历文件
            for file_path in folder.iterdir():
                if not file_path.is_file():
                    continue

                ext = file_path.suffix.lower()

                # 查找文件所属的分类（只在勾选的分类中查找）
                target_category = None
                for cat in selected_categories:
                    if ext in CATEGORIES.get(cat, []):
                        target_category = cat
                        break

                if not target_category:
                    continue  # 不属于勾选的类型，跳过

                # 创建目标文件夹
                target_dir = folder / target_category
                target_dir.mkdir(exist_ok=True)

                # 处理重名
                dest_path = target_dir / file_path.name
                if dest_path.exists():
                    name = file_path.stem
                    counter = 1
                    while dest_path.exists():
                        dest_path = target_dir / f"{name}_{counter}{ext}"
                        counter += 1
                    self.result_text.insert(tk.END, f"⚠️  重命名: {file_path.name} -> {dest_path.name}\n")

                # 移动文件
                try:
                    shutil.move(str(file_path), str(dest_path))
                    self.result_text.insert(tk.END, f"✅ 移动: {file_path.name} -> {target_category}/\n")
                    moved_count += 1
                except Exception as e:
                    self.result_text.insert(tk.END, f"❌ 失败: {file_path.name} - {str(e)}\n")
                    error_count += 1

                # 实时更新显示
                self.result_text.see(tk.END)
                self.root.update()

            # 完成总结
            self.result_text.insert(tk.END, "\n" + "=" * 50 + "\n")
            self.result_text.insert(tk.END, f"✅ 整理完成！\n")
            self.result_text.insert(tk.END, f"📁 成功移动: {moved_count} 个文件\n")
            if error_count > 0:
                self.result_text.insert(tk.END, f"❌ 失败: {error_count} 个文件\n")

            messagebox.showinfo("完成", f"整理完成！\n成功移动 {moved_count} 个文件")

        except Exception as e:
            messagebox.showerror("错误", f"整理过程中出现错误:\n{str(e)}")
        finally:
            # 恢复按钮
            self.organize_btn.config(state="normal", text="开始整理")


if __name__ == "__main__":
    root = tk.Tk()
    app = DesktopOrganizer(root)
    root.mainloop()