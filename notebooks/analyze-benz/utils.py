from IPython.display import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib import rcParams
import obspy
import os
pj = os.path.join
import io
from PIL import Image
import pathlib
from multiprocessing import Pool
import tqdm

SIZE_INCHES = (13, 8)
SIZE_PIX = (1000, 450)
# read images
def plot_images(images, show=True):
    # figure size in inches optional
    rcParams['figure.figsize'] = 13, 8

    length = len(images)
    fig, ax = plt.subplots(1, length)
    
    for i in range(length):
        image = images[i]
        ax[i].set_axis_off()
        ax[i].set_title(image.split('/')[-1])
        img = mpimg.imread(image)
        ax[i].imshow(img)
        
    return fig
        
def plot_waveform(waveform, show=True):
    # figure size in inches optional
    wf = obspy.read(waveform)
    wf = wf.filter('bandpass', freqmin=1, freqmax=15)
    fig = wf.plot(size=SIZE_PIX, handle=True)
    return fig


def images_and_waveform(path):
    filenames = os.listdir(path)
    files = [pj(path, filename) for filename in filenames]
    images = tuple(filter(lambda file: file.endswith('.png'), files))
    mseed = list(filter(lambda file: file.endswith('.mseed'), files))[0] 
    return images, mseed

def generate_data(df):
    """ Df must contain a column called 'Filepath' and 'Name' """
    for i, row in df.iterrows():
        yield images_and_waveform(row['Filepath']) + (row['Name'],)

def visualize(df, show=1):
    """  """
    for i, (images, waveform, name) in enumerate(generate_data(df)):
        print(name)
        plot_images(images)
        plot_waveform(waveform)
        
        if i % show == 0 and i > 0:
            yield  

def figure_to_image(figure):
    buf = io.BytesIO()
    figure.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    return img

def combine_images_vertical(images, y_offset=0):
    widths, heights = zip(*(i.size for i in images))
    max_width = max(widths)
    total_height = sum(heights)

    image = Image.new('RGB', (max_width, total_height + y_offset), color=(255,255,255,0))
    
    vert_pos = y_offset
    for im in images:
        width, height = im.size
        image.paste(im, (0, vert_pos))
        vert_pos += height + y_offset

    return image      
            
def write_visualization(folder_path, write_path):
    """
    :param folder_path: Path to the spectrogram and waveform
    """
    
    # Write folder
    dirname = os.path.dirname(write_path)
    pathlib.Path(dirname).mkdir(parents=True, exist_ok=True) 

    # Write images
    images, waveform = images_and_waveform(folder_path)
    
    fig1 = plot_images(images, show=False)
    plt.tight_layout()
    img1 = figure_to_image(fig1)
    
    fig2 = plot_waveform(waveform, show=False)
    img2 = figure_to_image(fig2)
    
    img = combine_images_vertical([img1, img2], y_offset=-100)
    img.save(write_path)

    
def _write_visualization_parallel(args):
    """
    Takes args as a tuple to work with imap_unordered
    """
    return write_visualization(*args)
    
def write_visualization_parallel(folder_paths, write_paths):
    args = list(zip(folder_paths, write_paths))
    pool = Pool()
    for _ in tqdm.tqdm(pool.imap_unordered(_write_visualization_parallel, args), total=len(args)):
        pass
