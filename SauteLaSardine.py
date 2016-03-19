from kivy.graphics import Line
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.config import Config
from kivy.clock import Clock
from kivy.uix.image import Image
from random import randint




class Pio(Widget):

    line = None
    image = None
    velocity = [0,0]
    accel = [0, -20.81]

    def build(self):
        with self.canvas:
            self.line = Line(points=[500,100,500,200], width=5)
            self.image = Image(source='visage.png',pos=(-120, 0),size=(120, 240))
            self.reposImage()
            ## return self.image

    def reposImage(self):
        self.image.pos = self.line.points[0],self.line.points[1]

    def on_touch_move(self, touch):
        ##if touch.x < self.width / 3:
        self.change_center(self.get_center()[0], touch.y)



        print("Touched: %s." % touch)

    def get_center(self):
        """
        :return: the barycenter coordinates
        """
        points = self.line.points
        x,y=0,0
        i=0
        while 2*i<len(points):
            x = x+points[2*i]
            y = y+points[2*i+1]
            i= i+1
        return [int(x/i), int(y/i)]

    def change_center(self, x,y):
        center = self.get_center()
        delta = x-center[0], y-center[1]
        self.move_by(delta)

    def move_by(self,delta):
        points = self.line.points
        i=0
        while 2*i<len(points):
            points[2*i]= delta[0]+points[2*i]
            points[2*i+1] =delta[1]+points[2*i+1]
            i= i+1
        self.line.points = self.line.points
        self.reposImage()

    def lowest_point(self):
        points = self.line.points
        lowest = [points[0], self.canvas.height]
        i=0
        while 2*i<len(points):
            if points[2*i+1]<lowest[1]:
                lowest = [points[2*i],points[2*i+1]]
        return lowest


    def move_on(self,step_time):
        ## bump?
        ## (for now, the lowest point is the first)
        foot = self.line.points[0],self.line.points[1]
        ##  we assume the paysageis a polygonal line that always grows to the right)
        ppoints = self.paysage.brokenLine.points
        ## go through the segments, measure if behind the x's
        i = 1
        while 2*i<len(ppoints):
             if foot[0] > ppoints[2*(i-1)] and foot[0]<ppoints[2*i]:
                ## we're behind the x's, are we below?
                ratio = (foot[0] - ppoints[2*(i-1)])/(ppoints[2*i]-ppoints[2*(i-1)])
                y = ppoints[2*(i-1)+1] + ratio* (ppoints[2*i+1]-ppoints[2*(i-1)+1])
                if y>foot[1]:
                    self.bump(y-foot[1])
             i=i+1


        ## adapt velocity based on accel
        self.velocity[0] = self.velocity[0]+step_time*self.accel[0]
        self.velocity[1] = self.velocity[1]+step_time*self.accel[1]

        ## adapt position based on velocity
        center = self.get_center()
        new_center = center[0]+step_time*self.accel[0],center[1]+step_time*self.accel[1]
        self.change_center(new_center[0],new_center[1])


    def bump(self, depth):
        print("bump!")
        Sounds.bumpSound.play()
        self.move_by([0,depth])






class Paysage(Widget):
    """
    A slowly moving landscape towards the left.
    """
    brokenLine = None
    brokenLineSteps = [0,10,0,0,50,0,0,20,30,50,0,10,50,100,20,0,0,10,20,10]
    brokenLineLength = 0
    screenWidth = 500


    def build_broken_line(self):
        brokenLineSlope = 0.0 # number of y pixels per x pixel
        points = []
        step = 50
        x,base_y = 200,200
        for h in Paysage.brokenLineSteps:
            points.append(x)
            x = x + step
            base_y = base_y + int(brokenLineSlope*step)
            points.append(base_y+h)
        with self.canvas:
            line = Line(points=points, width=2)
        self.brokenLine = line
        return line




    def move_on(self, velocity):
        points = self.brokenLine.points
        for i in range(0,len(points)):
            points[i] = points[i] = points[i] + velocity[i % 2]

        k = 0
        while k*2 < len(Paysage.brokenLineSteps):
            if points[2*k]<0:
             points[2*k] = points[2*k]+Paysage.screenWidth
            k = k+1


        # don't joke me, the below line will indeed attract the interest of kivy to redraw
        self.brokenLine.points = points


class TheGame(Widget):
    paysage = None
    velocity = None

    time = 0


    def launch_moves(self, vel=(-10, -1)):
        self.velocity = vel
        self.paysage = Paysage()
        self.add_widget(self.paysage)
        self.paysage.build_broken_line()



    def update(self, dt):
        self.time = self.time+1
        if self.time % 10 == 0:
            # adjust points of the triangle
            self.paysage.move_on(self.velocity)
            self.pio.move_on(2.0/1.0)
        pass



class Sounds:

    bumpSound = SoundLoader.load("sounds/hitting-wooden-pole-pdsounds-stephan.wav")

class SauteLaSardineApp(App):
    def build(self):
        game = TheGame()
        game.launch_moves()
        game.pio = Pio()
        game.add_widget(game.pio)
        game.pio.build()
        game.pio.paysage = game.paysage
        Paysage.screenWidth = Config.getint('graphics','width')
        Clock.schedule_interval(game.update, 1.0/60.0)

        return game


if __name__ == '__main__':
    SauteLaSardineApp().run()



