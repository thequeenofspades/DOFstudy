#Don't even bother unless you know what you are doing
#Note: the green texts are strings, not comments

import viz
import vizact

#simple texture shader, no lighting:
class texShader:
	def __init__(self):
		fragS = """
uniform sampler2D Texture;
varying vec3 pos;
varying vec3 normal;
varying vec3 worldpos;
void main()
{
	//Hack to get mirror working
	if(pos.y < -4.05) 
	{
		discard;
		return;
	}
	vec4 diffuse = texture2D(Texture, gl_TexCoord[0].st);
	gl_FragColor = diffuse;
	
}
"""
		vertS = """
varying vec3 normal;
varying vec3 pos;
varying vec3 worldpos;
uniform mat4 osg_ViewMatrix;
uniform mat4 osg_ViewMatrixInverse;

void main()
{
	gl_Position = ftransform();
	pos = vec3(gl_Vertex);
	worldpos = vec3(osg_ViewMatrixInverse * gl_Position);
	gl_TexCoord[0] = gl_MultiTexCoord0;
	normal = normalize(gl_NormalMatrix * gl_Normal);
}
"""
		self.shader = viz.addShader(0, vert = vertS, frag = fragS)
		self.shader.attach(viz.addUniformInt('Texture', 0))
	def applyShader(self, node):
		node.apply(self.shader)


#Applies texture and light from a single direction (parallel rays)
class lightShader:
	def __init__(self):
		fragS = """
uniform sampler2D Texture;
varying vec3 lightDir;
varying vec3 pos;
varying vec3 normal;
varying vec3 worldpos;
uniform vec3 Specular;
uniform vec3 LightColor;
uniform float Shiny;

void main()
{
	float dist = length(pos);
	vec3 liDi = normalize(lightDir);
	vec3 norm = normalize(normal);
	float nDotL = dot(norm, liDi);
	vec3 v = normalize(liDi-pos);
	float vDotN = dot(v, normal);
	float specShade = pow(clamp(vDotN, 0.0, 1.0), Shiny); 
	float diffShade = nDotL * 0.5 + 0.5;
	vec4 diffuse = texture2D(Texture, gl_TexCoord[0].st) * vec4(LightColor,1.0);
	gl_FragColor = vec4(diffuse.rgb * diffShade + Specular * specShade, diffuse.a);
}
"""
		vertS = """
varying vec3 normal;
varying vec3 pos;
varying vec3 worldpos;
varying vec3 lightDir;
uniform vec3 LightPos;
uniform vec3 LightColor;
uniform mat4 osg_ViewMatrix;
uniform mat4 osg_ViewMatrixInverse;

void main()
{
	vec3 LiNorm = normalize(LightPos);
	vec4 lp = vec4(LiNorm, 0.0);
	lp = osg_ViewMatrix * lp;
	lightDir = normalize(vec3(lp));
	gl_Position = ftransform();
	pos = vec3(gl_Position);
	worldpos = vec3(osg_ViewMatrixInverse * gl_Position);
	gl_TexCoord[0] = gl_MultiTexCoord0;
	normal = normalize(gl_NormalMatrix * gl_Normal);
}
"""
		self.specular = [0.0, 0.0, 0.0]
		self.shiny = 100
		self.lightPos = [0.0, 1.0, 0.0]
		self.lightColor = [0.4, 0.4, 0.4]
		self.shader = viz.addShader(0, vert = vertS, frag = fragS)
		self.shader.attach(viz.addUniformInt('Texture', 0))
	def setSpecular(self, spec, shiny ):
		self.specular = spec
	def setLightDir(self, pos):
		self.lightPos = pos
	def setLightColor(self, color):
		self.lightColor = color
	def applyShader(self, node):
		self.shader.attach(viz.addUniformFloat('LightPos', self.lightPos))
		self.shader.attach(viz.addUniformFloat('Specular', self.specular))
		self.shader.attach(viz.addUniformFloat('Shiny', self.shiny))
		self.shader.attach(viz.addUniformFloat('LightColor', self.lightColor))
		node.apply(self.shader)


#heh
class funShader:
	def __init__(self):
		fragS = """
uniform sampler2D Texture;
uniform float osg_FrameTime;
varying vec3 pos;
varying vec3 normal;
varying vec3 worldpos;

float sinN(float a, float b, float time)
{
	float swap = fract(time+a+b);
	
	if(swap < 0.3)
		return 0.5 + sin(a*time + b)*0.5;
	else if(swap < 0.7)
		return 0.5 + sin(b*time + a)*0.5;
	else
		return 0.5 + sin(b*a + time)*0.5;
}
void main()
{
	vec2 coord = gl_TexCoord[0].st;
	float x = coord.x;
	float y = coord.y;
	float time = osg_FrameTime*0.2;
	float scale = 0.5;
	float i = 0.0;
	vec3 diffuse = vec3(0.0,0.0,0.0);
	while (i < 5.0)
	{
		i = i+1.0;
		diffuse += scale/i * vec3(sinN(i,time,x), 
							      sinN(i,time,y),
							      sinN(i,time,pos.z));
	}
	vec3 logo = vec3(texture2D(Texture, coord));
	gl_FragColor = vec4(diffuse*logo,1.0);
}
"""
		vertS = """
varying vec3 normal;
varying vec3 pos;
varying vec3 worldpos;
uniform mat4 osg_ViewMatrix;
uniform mat4 osg_ViewMatrixInverse;

void main()
{
	gl_Position = ftransform();
	pos = vec3(gl_Position);
	worldpos = vec3(osg_ViewMatrixInverse * gl_Position);
	gl_TexCoord[0] = gl_MultiTexCoord0;
	normal = normalize(gl_NormalMatrix * gl_Normal);
}
"""
		self.shader = viz.addShader(0, vert = vertS, frag = fragS)
		self.shader.attach(viz.addUniformInt('Texture', 0))

	def applyShader(self, node):
		node.apply(self.shader)
		


class skyShader:
	def __init__(self):
		fragS = """
uniform sampler2D Texture;
uniform float osg_FrameTime;
varying vec3 pos;
varying vec3 normal;
varying vec3 worldpos;
varying vec3 objpos;


void main()
{
	vec2 coord = gl_TexCoord[0].st;
	float t = osg_FrameTime;
	
	vec3 color = vec3(0.0,0.0,0.0);
	
	color += 0.5 * vec3(texture2D(Texture, coord));
	color += 0.25 * vec3(texture2D(Texture, fract(coord*2.0)));
	color += 0.125 * vec3(texture2D(Texture, fract(coord*4.0)));
	
	gl_FragColor = vec4(color,1.0);
}
"""
		vertS = """
varying vec3 normal;
varying vec3 pos;
varying vec3 objpos;
varying vec3 worldpos;
uniform mat4 osg_ViewMatrix;
uniform mat4 osg_ViewMatrixInverse;

void main()
{
	objpos = vec3(gl_Vertex);
	gl_Position = ftransform();
	pos = vec3(gl_Position);
	worldpos = vec3(osg_ViewMatrixInverse * gl_Position);
	gl_TexCoord[0] = gl_MultiTexCoord0;
	normal = normalize(gl_NormalMatrix * gl_Normal);
}
"""
		self.shader = viz.addShader(0, vert = vertS, frag = fragS)
		self.shader.attach(viz.addUniformInt('Texture', 0))

	def applyShader(self, node):
		node.apply(self.shader)
	
	

class tunShader:
	def __init__(self):
		fragS = """
uniform sampler2D Texture;
uniform float osg_FrameTime;
varying vec3 pos;
varying vec3 normal;
varying vec3 worldpos;
varying vec3 objpos;

void main()
{
	if(pos.z < 100)
	{
		float i = sin(objpos.z);
		gl_FragColor = vec4(0.9, 0.9, max(i, 0.6), i);
	}
	else
	{
		gl_FragColor = vec4(0.9, 0.9, 0.7, 0.25);
	}
}
"""
		vertS = """
varying vec3 normal;
varying vec3 pos;
varying vec3 objpos;
varying vec3 worldpos;
uniform mat4 osg_ViewMatrix;
uniform mat4 osg_ViewMatrixInverse;

void main()
{
	objpos = gl_Vertex;
	gl_Position = ftransform();
	pos = vec3(gl_Position);
	worldpos = vec3(osg_ViewMatrixInverse * gl_Position);
	gl_TexCoord[0] = gl_MultiTexCoord0;
	normal = normalize(gl_NormalMatrix * gl_Normal);
}
"""
		self.shader = viz.addShader(0, vert = vertS, frag = fragS)
		self.shader.attach(viz.addUniformInt('Texture', 0))

	def applyShader(self, node):
		node.apply(self.shader)
		
		
class partShader:
	def __init__(self):
		fragS = """
uniform sampler2D Texture;
uniform float osg_FrameTime;
varying vec3 pos;
varying vec3 normal;
varying vec3 worldpos;
varying vec3 objpos;
uniform vec3 color;
uniform vec3 light;

void main()
{
	vec2 coord = gl_TexCoord[0].st*2.0 - vec2(1.0,1.0);
	float radius = coord.x*coord.x + coord.y*coord.y;
	float shade = dot(normal,light)*0.5 + 1.0;
	gl_FragColor = vec4(color*shade, (1.0-radius)/1.0);
}
"""
		vertS = """
varying vec3 normal;
varying vec3 pos;
varying vec3 objpos;
varying vec3 worldpos;
uniform vec3 lightDir;
uniform mat4 osg_ViewMatrix;
varying vec3 light;

void main()
{
	light = normalize(vec3(osg_ViewMatrix * vec4(lightDir,1.0)));
	objpos = gl_Vertex;
	gl_Position = ftransform();
	pos = vec3(gl_Position);
	gl_TexCoord[0] = gl_MultiTexCoord0;
	normal = normalize(gl_NormalMatrix * gl_Normal);
}
"""
		self.shader = viz.addShader(0, vert = vertS, frag = fragS)
		self.color = [1.0, 1.0, 1.0]
		self.lightDir = [0.0, -1.0, 0.0]
	def setColor(self, col):
		self.color = col
	def setLightDir(self, dir):
		self.lightDir = dir
	def applyShader(self, node):
		self.shader.attach(viz.addUniformInt('Texture', 0))
		self.shader.attach(viz.addUniformFloat('color', self.color))
		self.shader.attach(viz.addUniformFloat('lightDir', self.lightDir))
		node.apply(self.shader)

