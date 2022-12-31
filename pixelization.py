#!/usr/bin/python

import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
from models.networks import define_G
import glob

class Model():
    def __init__(self, device="cuda"):
        self.device = torch.device(device)
        self.G_A_net = None
        self.alias_net = None
        self.ref_t = None

    def load(self):
        with torch.no_grad():
            self.G_A_net = define_G(3, 3, 64, "c2pGen", "instance", False, "normal", 0.02, [0])
            self.alias_net = define_G(3, 3, 64, "antialias", "instance", False, "normal", 0.02, [0])

            G_A_state = torch.load("160_net_G_A.pth", map_location=str(self.device))
            for p in list(G_A_state.keys()):
                G_A_state["module."+str(p)] = G_A_state.pop(p)
            self.G_A_net.load_state_dict(G_A_state)

            alias_state = torch.load("alias_net.pth", map_location=str(self.device))
            for p in list(alias_state.keys()):
                alias_state["module."+str(p)] = alias_state.pop(p)
            self.alias_net.load_state_dict(alias_state)

            ref_img = Image.open("reference.png").convert('L')
            self.ref_t = process(greyscale(ref_img)).to(self.device)

    def pixelize(self, in_img, out_img):
        with torch.no_grad():
            in_img = Image.open(in_img).convert('RGB')
            in_t = process(in_img).to(self.device)
        
            out_t = self.alias_net(self.G_A_net(in_t, self.ref_t))

            save(out_t, out_img)

def greyscale(img):
    gray = np.array(img.convert('L'))
    tmp = np.expand_dims(gray, axis=2)
    tmp = np.concatenate((tmp, tmp, tmp), axis=-1)
    return Image.fromarray(tmp)

def process(img):
    ow,oh = img.size

    nw = int(round(ow / 4) * 4)
    nh = int(round(oh / 4) * 4)

    left = (ow - nw)//2
    top = (oh - nh)//2
    right = left + nw
    bottom = top + nh

    img = img.crop((left, top, right, bottom))

    trans = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

    return trans(img)[None, :, :, :]

def save(tensor, file):
    img = tensor.data[0].cpu().float().numpy()
    img = (np.transpose(img, (1, 2, 0)) + 1) / 2.0 * 255.0
    img = img.astype(np.uint8)
    Image.fromarray(img).save(file)


def pixelize_cli():
    import argparse
    import os
    parser = argparse.ArgumentParser(description='Pixelization')
    parser.add_argument('--input', type=str, default=None, required=True, help='path to image or directory')
    parser.add_argument('--output', type=str, default=None, required=False, help='path to save image/images')
    parser.add_argument('--cpu', action='store_true', help='use CPU instead of GPU')

    args = parser.parse_args()
    in_path = args.input
    out_path = args.output
    use_cpu = args.cpu

    if not os.path.exists("alias_net.pth"):
        print("missing models")

    pairs = []

    if os.path.isdir(in_path):
        in_images = glob.glob(in_path + "/*.png") + glob.glob(in_path + "/*.jpg")
        if not out_path:
            out_path = os.path.join(in_path, "outputs")
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        elif os.path.isfile(out_path):
            print("output cant be a file if input is a directory")
            return
        for i in in_images:
            pairs += [(i, i.replace(in_path, out_path))]
    elif os.path.isfile(in_path):
        if not out_path:
            base, ext = os.path.splitext(in_path)
            out_path = base+"_pixelized"+ext
        else:
            if os.path.isdir(out_path):
                _, file = os.path.split(in_path)
                out_path = os.path.join(out_path, file)
        pairs = [(in_path, out_path)]
    
    m = Model(device = "cpu" if use_cpu else "cuda")
    m.load()
    
    for in_file, out_file in pairs:
        print("PROCESSING", in_file, "TO", out_file)
        m.pixelize(in_file, out_file)

if __name__ == "__main__":
    pixelize_cli()