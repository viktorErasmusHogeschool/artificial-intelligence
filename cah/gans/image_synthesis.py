import torch
import torch.nn.parallel
import torch.utils.data
import torchvision.utils as vutils
from torchvision.utils import save_image
import pandas as pd
from . import Generator


def gen_image(text: str) -> bool:
    # check if phrase has a model attached to it
    df = pd.read_json("./data/cah-cards-full.json")
    phrase_row = df[df['text'] == text]
    PATH = phrase_row['path_to_model'].values[0]

    if PATH == 'not_available':
        print("No model associated to card: {}".format(text))
        return False

    else:
        # load model from path
        nz = 100

        try:
            state = torch.load(PATH)
            netG = Generator(0).to("cpu")
            netG.load_state_dict(state['model_state_dict'])

            # Choose how many images you want to plot and create a grid
            n_images = 1
            fixed_noise = torch.randn(n_images, nz, 1, 1, device="cpu")
            gen_img = netG(fixed_noise).detach().cpu()
            img_to_show = vutils.make_grid(gen_img, padding=2, normalize=True)
            save_image(img_to_show, 'gan.jpg')

        except Exception as e:
            print("Received '{}' but no associated GAN was found in Models. Raised exception: {}".format(text, e))

        return True
