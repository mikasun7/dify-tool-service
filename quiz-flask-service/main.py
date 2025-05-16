from flask import Flask, request, send_from_directory, jsonify, render_template, render_template_string

import os
import markdown
import time

app = Flask(__name__, static_folder='app/static', template_folder='app/templates')

# 配置文件夹路径
UPLOAD_FOLDER = './markdown-quiz-files'
OUTPUT_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# 确保文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/upload_markdown', methods=['POST'])
def upload_markdown():
    content = request.get_data(as_text=True)
    print("content:\n", content)
    if content is None:
        return jsonify({"error": "Invalid input"}), 400
    """Render quiz in Markdown format to HTML."""
    extensions = [
        "tables", "app.extensions.checkbox", "app.extensions.radio",
        "app.extensions.textbox"
    ]
    
    html = markdown.markdown(content, extensions=extensions, output_format="html5")

    # 使用 Flask 自带的 render_template_string 来渲染 HTML 片段
    print(app.jinja_loader.searchpath)
    base_html = render_template('base.html', content=html)
    final_html = render_template('wrapper.html', content=base_html)

    filename = str(int(time.time()))
    with open(os.path.join(OUTPUT_FOLDER, f"{filename}.html"), "w+", encoding='utf-8') as f:
        f.write(final_html)

    return jsonify(
        {"message":
         f"http://127.0.0.1:5006/get_html/{filename}"}), 200


@app.route('/get_html/<filename>', methods=['GET'])
def get_html(filename):
    if not filename.endswith('.html'):
        filename += '.html'

    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True, port=5006, host='0.0.0.0')
