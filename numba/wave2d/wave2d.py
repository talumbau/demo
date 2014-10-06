"""
    wave2d.py 
        
    Solve the 2D wave equation on a rectangle and make a movie of the solution

    Original Copyright (c) 2013 Greg von Winckel
    Modified by Stan Seibert <stan.seibert@continuum.io>

    Permission is hereby granted, free of charge, to any person obtaining
    a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
    TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

    Original Created on Sun Nov  3 17:20:21 MST 2013
"""



import matplotlib.pyplot as plt
import numpy as np
import matplotlib


class wave2d(object):
    def __init__(self,height,width,T,nx,ny,nt,c):
        self.nx = nx
        self.ny = ny
        self.nt = nt

        self.x = np.linspace(-0.5*width,0.5*width,nx)
        self.y = np.linspace(-0.5*height,0.5*height,ny)
        self.t = np.linspace(0,T,nt+1)

        self.dx = self.x[1]-self.x[0]
        self.dy = self.y[1]-self.y[0]
        self.dt = self.t[1]-self.t[0]
        
        self.xx,self.yy = np.meshgrid(self.x,self.y)

        # Gamma_x squared
        self.gx2 = c*self.dt/self.dx

        # Gamma_y squared
        self.gy2 = c*self.dt/self.dy

        # 2*(1-gamma_x^2-gamma_y^2)
        self.gamma = 2*(1 - self.gx2 - self.gy2)
        

    def solve(self,ffun,gfun,timesteps_func):

        f = ffun(self.xx,self.yy)
        g = gfun(self.xx,self.yy) 

        u = np.zeros((self.ny,self.nx,self.nt+1))

        # Set initial condition
        u[:,:,0] = f

        """ Compute first time step """
        u[:,:,1] = 0.5*self.gamma*f+self.dt*g
        u[1:-1,1:-1,1] += 0.5*self.gx2*(f[1:-1,2:]+f[1:-1,:-2])
        u[1:-1,1:-1,1] += 0.5*self.gy2*(f[:-2,1:-1]+f[2:,1:-1])

        timesteps_func(self.gamma, self.gx2, self.gy2, u)
        
        return u


def animate_solution(u):
    u_mapped = np.sign(u) * np.power(np.fabs(u), 0.333)
    fig = plt.figure()
    frame = plt.imshow(u_mapped[:,:,0], cmap=plt.get_cmap('coolwarm'), vmin=-1.0, vmax=1.0)

    def animate(i):
        frame.set_array(u_mapped[:,:,i])
        return frame,

    return matplotlib.animation.FuncAnimation(fig, animate, frames=u.shape[-1], interval=20)

