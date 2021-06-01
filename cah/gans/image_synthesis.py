import os
import random
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.optim as optim
import torch.utils.data
import torchvision.datasets as dset
import torchvision.transforms as transforms
import torchvision.utils as vutils
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np
import os

def gen_image(text):

    #check if phrase has a model attached to it
    df = pd.read_json("../data/cah-cards-full.json")
    phrase_row = df[df['text']== text]
    PATH = phrase_row['path_to_model']

    if PATH == 'not_available':
      return 0
    
    else:
        # Generator Code
        class Generator(nn.Module):
            def __init__(self, ngpu):
                super(Generator, self).__init__()
                self.ngpu = ngpu
                self.main = nn.Sequential(
                    # input is Z, going into a convolution
                    nn.ConvTranspose2d( nz, ngf * 8, 4, 1, 0, bias=False),
                    nn.BatchNorm2d(ngf * 8),
                    nn.ReLU(True),
                    # state size. (ngf*8) x 4 x 4
                    nn.ConvTranspose2d(ngf * 8, ngf * 4, 4, 2, 1, bias=False),
                    nn.BatchNorm2d(ngf * 4),
                    nn.ReLU(True),
                    # state size. (ngf*4) x 8 x 8
                    nn.ConvTranspose2d( ngf * 4, ngf * 2, 4, 2, 1, bias=False),
                    nn.BatchNorm2d(ngf * 2),
                    nn.ReLU(True),
                    # state size. (ngf*2) x 16 x 16
                    nn.ConvTranspose2d( ngf * 2, ngf, 4, 2, 1, bias=False),
                    nn.BatchNorm2d(ngf),
                    nn.ReLU(True),
                    # state size. (ngf) x 32 x 32
                    nn.ConvTranspose2d( ngf, nc, 4, 2, 1, bias=False),
                    nn.Tanh()
                    # state size. (nc) x 64 x 64
                )

            def forward(self, input):
                return self.main(input)


        #Load the trained generator
        nz = 100
        ngf = 64
        nc = 3
        state = torch.load(PATH)
        netG = Generator(0).to("cpu")
        netG.load_state_dict(state['model_state_dict'])

        #Choose how many images you want to plot and create a grid 
        n_images = 1
        fixed_noise = torch.randn(n_images, nz, 1, 1, device="cpu")
        gen_img = netG(fixed_noise).detach().cpu()
        img_to_show = np.transpose(vutils.make_grid(gen_img, padding=2, normalize=True),(1,2,0))

        # Plot the fake images from the generator
        #plt.figure(figsize=(8,8))
        #plt.axis("off")
        #plt.title(text)
        #plt.imshow(img_to_show)
        #plt.show()
        return 0



