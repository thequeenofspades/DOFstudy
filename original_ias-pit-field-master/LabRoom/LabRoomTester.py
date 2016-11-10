import viz
import LabRoom

viz.go()
viz.clearcolor(viz.SKYBLUE)

lab = LabRoom.LabRoom()
part = lab.getPart(LabRoom.DOOR3)
room = lab.getRoom()
part.setPosition([100,100,100])
