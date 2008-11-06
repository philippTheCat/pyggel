import pyggel
from pyggel import *

def main():
    pyggel.view.init()
    glDisable(GL_LIGHTING)
    camera = pyggel.camera.LookAtCamera((0,1,0), distance=10)
    camera2 = pyggel.camera.LookAtCamera((0,-1,0), distance=10)

    mesh = pyggel.mesh.OBJ("data/carrot.obj")
    poly1 = pyggel.math3d.Polygon(mesh.verts)

    s = pyggel.scene.Scene()
    s.add_3d(mesh)

    clock = pygame.time.Clock()
    while 1:
        camera.roty += 1
        camera2.roty += 1
        clock.tick(999)
        print clock.get_fps()
        for event in pyggel.get_events():
            if event.type == QUIT:
                pyggel.quit()
                return None

        s.render(camera)
        pyggel.view.set3d()
        camera2.push()
        mesh.render_collision_debug()
        camera2.pop()

        pyggel.view.refresh_screen()
main()
