import pygame, random, math, sys, array

# ============================================================
# GALAXY SURVIVOR - CLEAN EDITION
# Python 3.13 + Pygame 2.6.1 | One file | No external assets
# ============================================================
pygame.init()
try:
    pygame.mixer.init(22050, -16, 2, 512)
    AUDIO = True
except Exception:
    AUDIO = False

W, H = 1100, 800
FPS = 60
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("GALAXY SURVIVOR")
clock = pygame.time.Clock()

# ---------- Palette ----------
BG = (5, 8, 24); PANEL = (12, 18, 40); PANEL2 = (18, 26, 55)
WHITE = (242, 248, 255); MUTED = (130, 150, 185)
CYAN = (0, 230, 255); BLUE = (70, 125, 255); PINK = (255, 55, 160)
PURPLE = (180, 80, 255); GREEN = (55, 245, 135); YELLOW = (255, 220, 65)
RED = (255, 75, 90); ORANGE = (255, 145, 55)

F_SMALL = lambda n: pygame.font.SysFont("consolas", n, bold=True)
F_BIG = lambda n: pygame.font.SysFont("consolas", n, bold=True)

# ---------- Small procedural sounds ----------
def make_sound(a, b, ms, kind="sine", vol=.16):
    if not AUDIO:
        return None
    n = max(1, int(22050 * ms / 1000))
    buf = array.array("h", [0] * (n * 2))
    for i in range(n):
        t = i / 22050
        f = a + (b - a) * i / n
        if kind == "square": v = 1 if math.sin(2 * math.pi * f * t) > 0 else -1
        elif kind == "noise": v = random.uniform(-1, 1)
        else: v = math.sin(2 * math.pi * f * t)
        v *= (1 - i / n) * vol
        q = max(-32768, min(32767, int(v * 32767)))
        buf[i*2] = buf[i*2+1] = q
    try: return pygame.mixer.Sound(buffer=buf)
    except Exception: return None

SFX = {
    "click": make_sound(500, 850, 45, "sine", .15),
    "shoot": make_sound(950, 300, 55, "square", .12),
    "hit": make_sound(260, 80, 55, "noise", .14),
    "boom": make_sound(180, 25, 190, "noise", .25),
    "power": make_sound(420, 1200, 140, "sine", .18),
    "boss": make_sound(220, 55, 420, "square", .22),
    "win": make_sound(440, 900, 420, "sine", .18),
}

def play(name):
    if AUDIO and SFX.get(name): SFX[name].play()

def clamp(v, a, b): return max(a, min(b, v))

def txt(s, value, pos, size=20, color=WHITE, center=False):
    im = F_SMALL(size).render(str(value), True, color)
    r = im.get_rect(center=pos) if center else im.get_rect(topleft=pos)
    s.blit(im, r)
    return r

def glow(s, color, x, y, radius, alpha=80):
    size = radius * 2 + 8
    q = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(q, (*color, alpha // 3), (size//2, size//2), radius)
    pygame.draw.circle(q, (*color, alpha), (size//2, size//2), max(2, radius//2))
    s.blit(q, (x-size//2, y-size//2), special_flags=pygame.BLEND_ADD)

def panel(s, rect, accent=CYAN, alpha=225, radius=16):
    x, y, w, h = rect
    q = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(q, (*PANEL, alpha), (0, 0, w, h), border_radius=radius)
    pygame.draw.rect(q, (*accent, 150), (0, 0, w, h), 2, border_radius=radius)
    s.blit(q, (x, y))

def bar(s, x, y, w, h, value, maxv, color):
    pygame.draw.rect(s, (30, 38, 62), (x, y, w, h), border_radius=h//2)
    fill = int(w * clamp(value/maxv, 0, 1))
    if fill > 0: pygame.draw.rect(s, color, (x, y, fill, h), border_radius=h//2)

# ---------- Background ----------
class Star:
    def __init__(self, near=False):
        self.x = random.randrange(W); self.y = random.randrange(H)
        self.sp = random.uniform(1.2, 3.4) if near else random.uniform(.25, 1.0)
        self.r = random.choice([1,1,1,2]); self.a = random.random()*6.28
    def update(self, boost=1):
        self.y += self.sp * boost; self.a += .04
        if self.y > H+4: self.y=-4; self.x=random.randrange(W)
    def draw(self, s):
        tw = 170 + int(70*math.sin(self.a))
        pygame.draw.circle(s, (tw, min(255,tw+15), 255), (int(self.x),int(self.y)), self.r)

stars = [Star() for _ in range(125)] + [Star(True) for _ in range(55)]

def draw_background(s, t, theme=0, menu=False):
    themes = [((5,8,24),(40,35,110),CYAN), ((22,6,20),(100,20,75),PINK),
              ((4,18,28),(20,90,120),CYAN), ((6,24,16),(20,105,65),GREEN),
              ((15,7,28),(85,25,125),PURPLE)]
    base, neb, accent = themes[theme % len(themes)]
    s.fill(base)
    cloud = pygame.Surface((W,H), pygame.SRCALPHA)
    for i in range(6):
        x = (i*230 + 100 + math.sin(t*.22+i)*85) % (W+260) - 130
        y = 120 + math.cos(t*.18+i)*125
        pygame.draw.circle(cloud, (*neb, 30), (int(x), int(y)), 190)
    s.blit(cloud, (0,0))
    for st in stars: st.update(1.7 if not menu else 1); st.draw(s)
    # decorative orbital lines
    if menu:
        cx, cy = W//2, 180
        for r in (80, 112, 144):
            pygame.draw.ellipse(s, (*accent, 55), (cx-r, cy-r*.43, r*2, r*.86), 1)
        for k in range(3):
            a = t*(.7+k*.25) + k*2
            x = cx + math.cos(a)*112; y = cy + math.sin(a)*48
            glow(s, accent, int(x), int(y), 12, 80)
            pygame.draw.circle(s, WHITE, (int(x),int(y)), 3)
    # planet / moon
    px = 860; py = 180 + int(math.sin(t*.35)*12)
    glow(s, accent, px, py, 95, 35)
    pygame.draw.circle(s, (*neb, 100), (px,py), 88)
    pygame.draw.circle(s, (*accent, 90), (px-18,py-20), 62)
    pygame.draw.arc(s, (180,220,255), (px-105,py-35,210,80), .2, 2.9, 2)
    # fly-by UFO
    ux = int((t*105)%(W+180)-90); uy = 105+int(math.sin(t*1.5)*28)
    glow(s, accent, ux, uy, 28, 60)
    pygame.draw.ellipse(s, (45,55,82), (ux-30,uy-8,60,16))
    pygame.draw.ellipse(s, accent, (ux-17,uy-15,34,18), 2)
    pygame.draw.circle(s, WHITE, (ux,uy-7), 4)

# ---------- FX ----------
class Particle:
    def __init__(self,x,y,c,fast=False):
        self.x=x; self.y=y; self.c=c; a=random.random()*6.28
        sp=random.uniform(1.5,7 if fast else 4.5); self.vx=math.cos(a)*sp; self.vy=math.sin(a)*sp
        self.life=random.randint(18,38)
    def update(self): self.x+=self.vx; self.y+=self.vy; self.vx*=.98; self.vy*=.98; self.life-=1
    def draw(self,s):
        if self.life>0: glow(s,self.c,int(self.x),int(self.y),3,70)

class Bullet:
    def __init__(self,x,y,vx,vy,enemy=False,dmg=20,c=YELLOW):
        self.x=x; self.y=y; self.vx=vx; self.vy=vy; self.enemy=enemy; self.dmg=dmg; self.c=c
    def update(self): self.x+=self.vx; self.y+=self.vy
    def draw(self,s):
        pygame.draw.line(s,self.c,(int(self.x),int(self.y+8)),(int(self.x),int(self.y-8)),3)
        glow(s,self.c,int(self.x),int(self.y),7,100)

# ---------- Enemies ----------
class Enemy:
    DATA = {
        "DRONE": (18,45,CYAN,2.2), "SCOUT": (14,32,YELLOW,4.0),
        "TANK": (28,180,PURPLE,1.0), "HUNTER": (18,70,PINK,2.5),
        "ELITE": (25,260,RED,1.7),
    }
    def __init__(self,x,y,kind="DRONE",boss=False):
        self.x=x; self.y=y; self.home=x; self.kind=kind; self.boss=boss; self.t=random.random()*6.2
        self.shot=random.randint(50,100)
        if boss: self.r=62; self.maxhp=2200; self.c=PINK; self.sp=.55
        else: self.r,self.maxhp,self.c,self.sp=self.DATA[kind]
        self.hp=self.maxhp
    def update(self, px, py, enemy_bullets):
        self.t += .045
        if self.boss:
            self.y=min(150,self.y+self.sp); self.x=self.home+math.sin(self.t*.7)*300
        elif self.kind=="HUNTER":
            dx=px-self.x; dy=py-self.y; d=max(1,math.hypot(dx,dy)); self.x+=dx/d*self.sp; self.y+=dy/d*self.sp
        else:
            self.y+=self.sp; self.x=self.home+math.sin(self.t)*55
        self.shot-=1
        if self.shot<=0 and self.y>20:
            self.shot=28 if self.boss else random.randint(70,125)
            if self.boss:
                for ang in (-.55,-.28,0,.28,.55): enemy_bullets.append(Bullet(self.x,self.y+32,math.sin(ang)*5.5,math.cos(ang)*5.5,True,13,PINK))
            elif self.kind in ("TANK","ELITE"):
                enemy_bullets.append(Bullet(self.x,self.y+self.r,0,5.3,True,11,RED))
    def draw(self,s):
        x,y=int(self.x),int(self.y); glow(s,self.c,x,y,self.r+9,65)
        if self.boss:
            pygame.draw.ellipse(s,self.c,(x-70,y-25,140,52))
            pygame.draw.ellipse(s,(35,45,75),(x-38,y-18,76,30))
            pygame.draw.ellipse(s,WHITE,(x-18,y-22,36,25))
            for dx in (-48,48): pygame.draw.circle(s,self.c,(x+dx,y+8),8)
            pygame.draw.arc(s,WHITE,(x-58,y-30,116,60),0,math.pi,3)
        elif self.kind=="DRONE":
            pts=[(x,y-20),(x+25,y-2),(x+13,y+20),(x,y+10),(x-13,y+20),(x-25,y-2)]
            pygame.draw.polygon(s,self.c,pts); pygame.draw.polygon(s,WHITE,pts,2)
            pygame.draw.circle(s,WHITE,(x,y),5)
        elif self.kind=="SCOUT":
            pygame.draw.polygon(s,YELLOW,[(x,y-18),(x+20,y+12),(x,y+7),(x-20,y+12)])
            pygame.draw.circle(s,WHITE,(x,y-2),5)
        elif self.kind=="TANK":
            pygame.draw.circle(s,PURPLE,(x,y),self.r)
            pygame.draw.circle(s,(35,35,70),(x,y),self.r-8)
            pygame.draw.circle(s,PURPLE,(x,y),8)
            pygame.draw.line(s,PURPLE,(x-self.r,y),(x+self.r,y),3)
        elif self.kind=="HUNTER":
            pts=[(x,y-self.r),(x+self.r,y),(x,y+self.r),(x-self.r,y)]
            pygame.draw.polygon(s,PINK,pts); pygame.draw.polygon(s,WHITE,pts,2)
            pygame.draw.line(s,WHITE,(x-self.r//2,y),(x+self.r//2,y),2)
        else:
            pygame.draw.polygon(s,RED,[(x,y-self.r),(x+self.r,y-5),(x+12,y+self.r),(x-12,y+self.r),(x-self.r,y-5)])
            pygame.draw.circle(s,WHITE,(x,y),6)
        if self.hp<self.maxhp:
            bar(s,x-self.r,y-self.r-12,self.r*2,5,self.hp,self.maxhp,GREEN)

class UFO:
    def __init__(self,gold=False):
        self.x=-60; self.y=random.randint(100,300); self.gold=gold; self.hp=150 if gold else 80
        self.c=YELLOW if gold else CYAN
    def update(self): self.x += 5.5 if self.gold else 3.2
    def draw(self,s):
        x,y=int(self.x),int(self.y); glow(s,self.c,x,y,34,70)
        pygame.draw.ellipse(s,self.c,(x-32,y-11,64,22)); pygame.draw.ellipse(s,(40,45,75),(x-16,y-20,32,17))
        pygame.draw.ellipse(s,WHITE,(x-10,y-16,20,11))

class Drop:
    COLORS={"COIN":YELLOW,"SHIELD":CYAN,"HEAL":GREEN,"RAPID":PINK,"TRIPLE":PURPLE}
    def __init__(self,x,y,k): self.x=x; self.y=y; self.k=k; self.t=random.random()*6
    def update(self): self.y+=1.5; self.t+=.08
    def draw(self,s):
        c=self.COLORS[self.k]; x,y=int(self.x),int(self.y); glow(s,c,x,y,18,80)
        pygame.draw.circle(s,c,(x,y),12,2); txt(s,self.k[0],(x,y-7),10,WHITE,True)

# ---------- Ship artwork ----------
def draw_ship(s,x,y,variant=0,tilt=0,engine=True,scale=1.0):
    c=[CYAN,PURPLE,YELLOW][variant%3]; x=int(x); y=int(y)
    glow(s,c,x,y+8,int(40*scale),85)
    # engine flames
    if engine:
        flame=8+int(abs(math.sin(pygame.time.get_ticks()/90))*7)
        pygame.draw.polygon(s,YELLOW,[(x-9,y+29),(x,y+29+flame),(x+9,y+29)])
        pygame.draw.polygon(s,WHITE,[(x-4,y+29),(x,y+25+flame),(x+4,y+29)])
    # wide futuristic wings
    wing=[(x-8,y-5),(x-45,y+18),(x-29,y+25),(x-14,y+17),(x,y+30),(x+14,y+17),(x+29,y+25),(x+45,y+18),(x+8,y-5)]
    pygame.draw.polygon(s,(25,35,68),wing); pygame.draw.polygon(s,c,wing,3)
    pygame.draw.polygon(s,c,[(x,y-42),(x-18,y+12),(x-10,y+8),(x,y+24),(x+10,y+8),(x+18,y+12)])
    pygame.draw.polygon(s,WHITE,[(x,y-42),(x-18,y+12),(x,y+24),(x+18,y+12)],2)
    pygame.draw.ellipse(s,(205,245,255),(x-9,y-20,18,25))
    pygame.draw.line(s,c,(x-28,y+16),(x-10,y+10),3); pygame.draw.line(s,c,(x+28,y+16),(x+10,y+10),3)
    # engine lights
    pygame.draw.circle(s,WHITE,(x-23,y+21),3); pygame.draw.circle(s,WHITE,(x+23,y+21),3)

# ---------- Game ----------
class Game:
    def __init__(self):
        self.state="MENU"; self.t=0; self.theme=0; self.ship=0
        self.score=0; self.coins=0; self.wave=1; self.hp=100; self.shield=60
        self.ai=False; self.combo=0; self.cool=0; self.energy=0
        self.rapid=0; self.triple=0; self.msg=""; self.msgtime=0; self.msgc=CYAN
        self.px=W//2; self.py=H-110; self.enemies=[]; self.ufos=[]; self.drops=[]
        self.bullets=[]; self.ebullets=[]; self.parts=[]; self.flash=0
        self.spawn_wave()
    def say(self,m,c=CYAN): self.msg=m; self.msgtime=100; self.msgc=c
    def reset(self):
        self.state="PLAY"; self.score=0; self.coins=0; self.wave=1; self.hp=100; self.shield=60
        self.ai=False; self.combo=0; self.cool=0; self.energy=0; self.rapid=0; self.triple=0
        self.px=W//2; self.py=H-110; self.enemies=[]; self.ufos=[]; self.drops=[]; self.bullets=[]; self.ebullets=[]; self.parts=[]
        self.spawn_wave(); play("click")
    def spawn_wave(self):
        self.theme=(self.wave-1)%5
        if self.wave%5==0:
            self.enemies.append(Enemy(W//2,-80,boss=True)); self.say("WARNING  //  MOTHERSHIP DETECTED",PINK); play("boss")
        else:
            types=["DRONE"]
            if self.wave>=2: types.append("SCOUT")
            if self.wave>=3: types.append("HUNTER")
            if self.wave>=4: types.append("TANK")
            if self.wave>=6: types.append("ELITE")
            for _ in range(5+self.wave*2): self.enemies.append(Enemy(random.randint(55,W-55),random.randint(-600,-50),random.choice(types)))
        if random.random()<.75: self.ufos.append(UFO(random.random()<.2))
    def shoot(self):
        if self.cool>0: return
        self.cool=5 if self.rapid>0 else 9
        spread=(-14,14) if self.triple>0 else (0,)
        for dx in spread: self.bullets.append(Bullet(self.px+dx,self.py-35,0,-15,False,26,YELLOW))
        play("shoot")
    def damage(self,d):
        if self.shield>0: self.shield=max(0,self.shield-d)
        else: self.hp=max(0,self.hp-d)
        self.flash=8
    def explode(self,x,y,c,big=False):
        play("boom" if big else "hit")
        for _ in range(28 if big else 12): self.parts.append(Particle(x,y,c,big))
    def move(self,keys):
        if self.ai:
            targets=self.enemies+self.ufos
            if targets:
                target=min(targets,key=lambda e:abs(e.x-self.px))
                self.px += (target.x-self.px)*.075
                self.py += ((H-145)-self.py)*.025
        else:
            sp=7
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.px-=sp
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.px+=sp
            if keys[pygame.K_w] or keys[pygame.K_UP]: self.py-=sp
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.py+=sp
        self.px=clamp(self.px,45,W-45); self.py=clamp(self.py,90,H-45)
    def update(self):
        self.t+=.04
        for p in self.parts[:]:
            p.update()
            if p.life<=0: self.parts.remove(p)
        if self.msgtime>0: self.msgtime-=1
        if self.flash>0: self.flash-=1
        if self.state!="PLAY": return
        keys=pygame.key.get_pressed(); self.move(keys)
        if self.cool>0: self.cool-=1
        if self.rapid>0:self.rapid-=1
        if self.triple>0:self.triple-=1
        if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0] or self.ai: self.shoot()
        for b in self.bullets[:]:
            b.update()
            if b.y<-40: self.bullets.remove(b)
        for e in self.enemies[:]:
            e.update(self.px,self.py,self.ebullets)
            if e.y>H+70 and not e.boss:
                self.enemies.remove(e); self.damage(10); continue
            for b in self.bullets[:]:
                if math.hypot(e.x-b.x,e.y-b.y)<e.r+7:
                    self.bullets.remove(b); e.hp-=b.dmg; play("hit")
                    if e.hp<=0:
                        gain=500 if e.boss else 100+self.combo*8; self.score+=gain; self.combo+=1; self.energy=min(100,self.energy+8)
                        self.explode(e.x,e.y,e.c,e.boss)
                        if random.random()<.3 and not e.boss: self.drops.append(Drop(e.x,e.y,random.choice(list(Drop.COLORS))))
                        if e in self.enemies:self.enemies.remove(e)
                        break
        for u in self.ufos[:]:
            u.update()
            for b in self.bullets[:]:
                if math.hypot(u.x-b.x,u.y-b.y)<25:
                    self.bullets.remove(b); u.hp-=b.dmg
                    if u.hp<=0:
                        self.score+=250; self.coins+=10; self.explode(u.x,u.y,u.c,True); self.ufos.remove(u); break
            if u.x>W+80 and u in self.ufos:self.ufos.remove(u)
        for b in self.ebullets[:]:
            b.update()
            if math.hypot(b.x-self.px,b.y-self.py)<24:
                self.damage(b.dmg); self.ebullets.remove(b); self.explode(self.px,self.py,RED)
            elif b.y>H+30:self.ebullets.remove(b)
        for d in self.drops[:]:
            d.update()
            if math.hypot(d.x-self.px,d.y-self.py)<30:
                if d.k=="COIN": self.coins+=15
                elif d.k=="SHIELD": self.shield=min(100,self.shield+35)
                elif d.k=="HEAL": self.hp=min(100,self.hp+25)
                elif d.k=="RAPID": self.rapid=420
                elif d.k=="TRIPLE": self.triple=420
                play("power"); self.drops.remove(d)
        if not self.enemies:
            self.wave+=1; self.combo=0; self.spawn_wave()
        if self.hp<=0: self.state="OVER"; play("boom")
    # ---------- UI ----------
    def button(self,s,label,rect,accent=CYAN):
        r=pygame.Rect(rect); hover=r.collidepoint(pygame.mouse.get_pos())
        fill=PANEL2 if not hover else (35,38,72)
        pygame.draw.rect(s,fill,r,border_radius=12); pygame.draw.rect(s,accent if hover else (70,95,135),r,2,border_radius=12)
        if hover: glow(s,accent,r.centerx,r.centery,28,35)
        txt(s,label,r.center,17,WHITE,True)
        return r
    def top_title(self,s):
        txt(s,"GALAXY",(W//2,55),30,CYAN,True); txt(s,"SURVIVOR",(W//2,84),38,WHITE,True)
    def menu(self,s):
        self.top_title(s)
        txt(s,"ALIEN FRONTIER  /  DEEP SPACE COMMAND",(W//2,120),13,MUTED,True)
        # central hero ship
        draw_ship(s,W//2,225,self.ship,scale=1.35)
        txt(s,"CHOOSE YOUR MISSION",(W//2,305),15,MUTED,True)
        self.button(s,"START MISSION",(360,330,380,54),CYAN)
        self.button(s,"SHIP GARAGE",(360,395,185,48),PURPLE)
        self.button(s,"HOW TO PLAY",(555,395,185,48),BLUE)
        self.button(s,"EXIT",(360,455,380,44),RED)
        # feature cards
        cards=[("ALIEN FLEET","5 enemy classes",PINK),("AUTO-PILOT","Press P / easy mode",GREEN),("BOSS WAVES","Mothership every 5",YELLOW)]
        for i,(a,b,c) in enumerate(cards):
            x=85+i*315; panel(s,(x,550,290,90),c,190,14); txt(s,a,(x+18,568),16,c); txt(s,b,(x+18,598),13,WHITE)
        txt(s,"WASD / ARROWS MOVE   •   SPACE FIRE   •   P AI   •   E ULTIMATE   •   ESC MENU",(W//2,690),12,MUTED,True)
    def garage(self,s):
        txt(s,"SHIP GARAGE",(W//2,62),36,WHITE,True); txt(s,"SELECT YOUR SURVIVOR",(W//2,95),13,MUTED,True)
        names=[("NOVA",CYAN,"BALANCED"),("VOID",PURPLE,"FAST + SHARP"),("TITAN",YELLOW,"HEAVY + POWER")]
        for i,(name,c,desc) in enumerate(names):
            x=90+i*335; r=pygame.Rect(x,145,300,430); panel(s,r,c,225,18)
            if self.ship==i: pygame.draw.rect(s,c,r,3,border_radius=18)
            draw_ship(s,x+150,280,i,scale=1.25)
            txt(s,name,(x+150,370),25,c,True); txt(s,desc,(x+150,400),13,WHITE,True)
            stats=[("SPEED",[8,10,6][i]),("ARMOR",[7,5,10][i]),("FIRE",[8,9,10][i])]
            for j,(lab,val) in enumerate(stats):
                txt(s,lab,(x+25,440+j*32),11,MUTED); bar(s,x+100,442+j*32,160,8,val,10,c)
            if self.ship==i: txt(s,"EQUIPPED",(x+150,545),13,GREEN,True)
            else: self.button(s,"SELECT",(x+85,530,130,38),c)
        self.button(s,"BACK TO COMMAND",(420,650,260,48),CYAN)
    def help(self,s):
        txt(s,"HOW TO PLAY",(W//2,58),36,WHITE,True); txt(s,"EVERYTHING YOU NEED BEFORE LAUNCH",(W//2,92),13,MUTED,True)
        items=[("01","MOVE","WASD or ARROW KEYS",CYAN),("02","FIRE","SPACE or LEFT MOUSE",YELLOW),
               ("03","AUTO-PILOT","PRESS P TO TOGGLE AI",GREEN),("04","ULTIMATE","PRESS E WHEN ENERGY IS 100%",PINK),
               ("05","POWERUPS","COLLECT SHIELD / HEAL / RAPID / TRIPLE",PURPLE),("06","BOSS","EVERY 5TH WAVE IS A MOTHERSHIP",RED)]
        for i,(num,head,desc,c) in enumerate(items):
            col=i%2; row=i//2; x=90+col*490; y=145+row*145
            panel(s,(x,y,450,115),c,220,16); txt(s,num,(x+20,y+18),13,c); txt(s,head,(x+62,y+16),20,WHITE); txt(s,desc,(x+62,y+52),13,MUTED)
            pygame.draw.line(s,c,(x+62,y+82),(x+390,y+82),2)
        self.button(s,"BACK TO COMMAND",(420,650,260,48),CYAN)
    def gameplay(self,s):
        # top status strip
        panel(s,(16,14,1068,76),CYAN,220,15)
        txt(s,"SCORE",(32,28),11,MUTED); txt(s,self.score,(32,48),20,WHITE)
        txt(s,"WAVE",(142,28),11,MUTED); txt(s,self.wave,(142,48),20,CYAN)
        txt(s,"COMBO",(220,28),11,MUTED); txt(s,"x"+str(self.combo),(220,48),20,YELLOW)
        # wave progress center
        target=max(1,5+self.wave*2); alive=sum(1 for e in self.enemies if not e.boss)
        progress=0 if any(e.boss for e in self.enemies) else 1-alive/target
        txt(s,"WAVE PROGRESS",(455,25),10,MUTED,True); bar(s,335,45,350,10,progress,1,CYAN)
        # AI control
        ai_rect=self.button(s,"AI AUTO  :  "+("ON" if self.ai else "OFF"),(900,27,165,38),GREEN if self.ai else BLUE)
        # left vitals
        panel(s,(18,108,255,145),GREEN,210,14)
        txt(s,"PILOT STATUS",(35,123),12,GREEN); txt(s,"HULL",(35,151),10,MUTED); bar(s,95,153,150,9,self.hp,100,GREEN); txt(s,str(self.hp)+"%",(35,168),13,WHITE)
        txt(s,"SHIELD",(35,198),10,MUTED); bar(s,95,200,150,9,self.shield,100,CYAN); txt(s,str(self.shield), (35,215),13,WHITE)
        # right loadout
        panel(s,(827,108,255,145),PURPLE,210,14)
        txt(s,"LOADOUT",(845,123),12,PURPLE)
        txt(s,"RAPID FIRE",(845,151),10,MUTED); txt(s,"READY" if self.rapid else "OFF",(1010,151),11,PINK,True)
        txt(s,"TRIPLE SHOT",(845,178),10,MUTED); txt(s,"READY" if self.triple else "OFF",(1010,178),11,PURPLE,True)
        txt(s,"ULTIMATE",(845,205),10,MUTED); bar(s,845,222,195,8,self.energy,100,PINK)
        # bottom command deck
        panel(s,(18,690,1064,92),BLUE,220,14)
        cards=[("MOVE","W A S D",CYAN),("FIRE","SPACE",YELLOW),("AI","P",GREEN),("ULTIMATE","E",PINK),("MENU","ESC",RED)]
        for i,(a,b,c) in enumerate(cards):
            x=35+i*205; txt(s,a,(x,708),11,c); txt(s,b,(x,731),15,WHITE)
        # objects
        for b in self.bullets:self._draw_bullet(s,b)
        for b in self.ebullets:self._draw_bullet(s,b)
        for e in self.enemies:e.draw(s)
        for u in self.ufos:u.draw(s)
        for d in self.drops:d.draw(s)
        draw_ship(s,self.px,self.py,self.ship,scale=1.0)
        if self.ai:
            pygame.draw.circle(s,GREEN,(int(self.px),int(self.py)),48,1); txt(s,"AI",(self.px,self.py+54),10,GREEN,True)
        if self.msgtime: txt(s,self.msg,(W//2,105),22,self.msgc,True)
        if self.flash: 
            q=pygame.Surface((W,H),pygame.SRCALPHA); q.fill((255,70,80,self.flash*8)); s.blit(q,(0,0))
    def _draw_bullet(self,s,b): b.draw(s)
    def over(self,s):
        # dark overlay
        q=pygame.Surface((W,H),pygame.SRCALPHA); q.fill((2,4,14,190)); s.blit(q,(0,0))
        panel(s,(300,170,500,420),PINK,240,22)
        txt(s,"MISSION FAILED",(W//2,230),38,PINK,True)
        txt(s,"THE GALAXY NEEDS A BETTER PILOT",(W//2,272),12,MUTED,True)
        txt(s,"SCORE",(390,330),11,MUTED); txt(s,self.score,(390,360),26,WHITE)
        txt(s,"WAVE",(650,330),11,MUTED); txt(s,self.wave,(650,360),26,CYAN)
        self.button(s,"RESTART MISSION",(370,425,360,48),CYAN)
        self.button(s,"COMMAND CENTER",(370,485,360,48),BLUE)
    def draw(self,s):
        draw_background(s,self.t,self.theme,self.state!="PLAY")
        for p in self.parts:p.draw(s)
        if self.state=="MENU": self.menu(s)
        elif self.state=="GARAGE": self.garage(s)
        elif self.state=="HELP": self.help(s)
        elif self.state=="PLAY": self.gameplay(s)
        elif self.state=="OVER": self.over(s)
    # ---------- Input ----------
    def click(self,pos):
        x,y=pos
        if self.state=="MENU":
            if pygame.Rect(360,330,380,54).collidepoint(pos): self.reset()
            elif pygame.Rect(360,395,185,48).collidepoint(pos): self.state="GARAGE"; play("click")
            elif pygame.Rect(555,395,185,48).collidepoint(pos): self.state="HELP"; play("click")
            elif pygame.Rect(360,455,380,44).collidepoint(pos): pygame.quit(); sys.exit()
        elif self.state=="GARAGE":
            for i in range(3):
                if pygame.Rect(90+i*335,145,300,430).collidepoint(pos): self.ship=i; play("click")
            if pygame.Rect(420,650,260,48).collidepoint(pos): self.state="MENU"; play("click")
        elif self.state=="HELP":
            if pygame.Rect(420,650,260,48).collidepoint(pos): self.state="MENU"; play("click")
        elif self.state=="PLAY":
            if pygame.Rect(900,27,165,38).collidepoint(pos): self.ai=not self.ai; play("click")
        elif self.state=="OVER":
            if pygame.Rect(370,425,360,48).collidepoint(pos): self.reset()
            elif pygame.Rect(370,485,360,48).collidepoint(pos): self.state="MENU"; play("click")
    def key(self,key):
        if key==pygame.K_ESCAPE:
            if self.state=="PLAY": self.state="MENU"
            elif self.state in ("GARAGE","HELP","OVER"): self.state="MENU"
            else: pygame.quit(); sys.exit()
        elif self.state=="PLAY":
            if key==pygame.K_p: self.ai=not self.ai; play("click")
            elif key in (pygame.K_e,pygame.K_LSHIFT) and self.energy>=100:
                self.energy=0; play("boom")
                for e in self.enemies[:]:
                    e.hp-=600
                    if e.hp<=0:
                        self.explode(e.x,e.y,e.c,e.boss); self.score+=500; self.enemies.remove(e)
        elif self.state=="OVER" and key in (pygame.K_RETURN,pygame.K_SPACE): self.reset()

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type==pygame.QUIT: pygame.quit(); return
                if e.type==pygame.KEYDOWN: self.key(e.key)
                if e.type==pygame.MOUSEBUTTONDOWN and e.button==1: self.click(e.pos)
            self.update()
            surf=pygame.Surface((W,H)); self.draw(surf)
            screen.blit(surf,(0,0)); pygame.display.flip(); clock.tick(FPS)

if __name__=="__main__": Game().run()
