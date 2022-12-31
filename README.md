## Inference script for [Pixelization](https://github.com/WuZongWei6/Pixelization)
All credit to those guys, I just stripped down thier code to make it simple to use.

## Usage
```
git clone https://github.com/arenatemp/pixelization_inference
pip install pillow torch torchvision numpy
```
Download the pretrained models into the pixelization_inference folder:
[pixelart_vgg19.pth](https://drive.google.com/file/d/1VRYKQOsNlE1w1LXje3yTRU5THN2MGdMM/view?usp=sharing)
[alias_net.pth](https://drive.google.com/file/d/17f2rKnZOpnO9ATwRXgqLz5u5AZsyDvq_/view?usp=sharing)
[160_net_G_A.pth](https://drive.google.com/file/d/1i_8xL3stbLWNF4kdQJ50ZhnRFhSDh3Az/view?usp=sharing)
```
python pixelization.py --input input_file.png
```