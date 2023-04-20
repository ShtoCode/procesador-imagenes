import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
from werkzeug.utils import secure_filename
from PIL import Image, ImageFilter, ImageEnhance

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/img'


SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and 'photo' in request.files:
        file = request.files['photo']
        size = request.form.get('size')
        brightness = int(request.form.get('brightness'))
        contrast = int(request.form.get('contrast'))
        saturation = int(request.form.get('saturation'))
        black_and_white = request.form.get('black_and_white')
        filter_blur = request.form.get("filter_blur")
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('process_image', filename=filename, size=size, brightness=brightness, contrast=contrast, saturation=saturation, black_and_white=black_and_white, filter_blur=filter_blur))

    return render_template('index.html')


@app.route('/process/<filename>')
def process_image(filename):
    size = request.args.get('size', 'original')
    if size == 'small':
        size = (300, 300)
    elif size == 'medium':
        size = (500, 500)
    elif size == 'large':
        size = (800, 800)
    else:
        size = None

    brightness = request.args.get('brightness', type=float) / 100
    contrast = request.args.get('contrast', type=float) / 100
    saturation = request.args.get('saturation', type=float) / 100

    black_and_white = 'black_and_white' in request.args

    filter_blur = 'filter_blur' in request.args

    image = Image.open('static/img/' + filename)

    
    if size is not None:
        image = image.resize(size)

    if black_and_white:
        image = image.convert('L')

    if filter_blur:
        image = image.filter(ImageFilter.GaussianBlur(radius=10))

    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness)

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)

    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(saturation)

    processed_filename = 'processed_' + filename

    image.save('static/img/' + processed_filename)

    brightness_percentage = int(brightness * 100)
    saturation_percentage = int(saturation * 100)
    contrast_percentage = int(saturation * 100)

    return render_template('process.html', original_filename=filename, processed_filename=processed_filename, brightness=brightness_percentage, saturation=saturation_percentage, contrast=contrast_percentage)


@app.route('/download/<filename>')
def download(filename):
    try:
        return send_from_directory('static/img', filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)


