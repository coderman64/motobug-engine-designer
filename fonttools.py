from sdl2 import *
from sdl2.sdlttf import *
import ctypes


def quickRenderText(rend,font,text,x,y):
    # convert text to a bytestring
    text = bytes(str(text),"ASCII")

    # take the draw color from the renderer and convert it to an SDL_Color
    r,g,b,a = ctypes.c_uint8(),ctypes.c_uint8(),ctypes.c_uint8(),ctypes.c_uint8()
    SDL_GetRenderDrawColor(rend,r,g,b,a)
    fontColor = SDL_Color()
    fontColor.r, fontColor.g, fontColor.b, fontColor.a = r,g,b,a

    # render the text and convert it to a texture
    textSurface = TTF_RenderText_Solid(font,text,fontColor)
    textTex = SDL_CreateTextureFromSurface(rend, textSurface)

    # calculate the bounding box for the final text placement 
    rect = SDL_Rect()
    textw, texth = ctypes.c_int(),ctypes.c_int()
    TTF_SizeText(font,text,textw,texth)
    rect.x, rect.y, rect.w, rect.h = x,y,textw.value, texth.value

    # copy the text texture to the renderer
    SDL_RenderCopy(rend, textTex, None, rect)

    # clear the texture (so we don't have any texture memory leaks)
    SDL_DestroyTexture(textTex)