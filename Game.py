#region Biblio et package utilisés
import datetime
import os
import socket
import threading
import time
import traceback
import sys

import arcade
from pyglet.image import load as pyglet_load

#endregion

#region sys multijoueur
class TaskThread:

    def __init__(self, Fonction, Args = None):
        """
        Passe une fonction (avec ou sans parametre) en arrière plan (ex : un while tournera en meme temps que le reste du script)

        ici : sys multi tournera en arriere plan
        """

        if Args != None:
            thread = threading.Thread(target = Fonction, args = Args)
        else:
            thread = threading.Thread(target = Fonction)
        thread.start()

class Client:
    def __init__(self) -> None:
        pass

class Server:
    def __init__(self) -> None:
        pass
#endregion

#region sys style console
class Colors:
    """
    Couleurs pour la console
    """

    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'

class Debug:
    """
    plus stylé pour la console
    """

    def Log(Text:str):
        print()
        print(Colors.OKGREEN + Text + Colors.ENDC)
        File.WriteFile(CurrentLogFile, "(" + str(CurrentTime.hour) + "_" + str(CurrentTime.minute) + "_" + str(CurrentTime.second) + ")" + " -- " + "[LOG] : " + Text)
    
    def Warn(Text:str):
        print()
        print(Colors.WARNING + Text + Colors.ENDC)
        File.WriteFile(CurrentLogFile, "(" + str(CurrentTime.hour) + "_" + str(CurrentTime.minute) + "_" + str(CurrentTime.second) + ")" + " -- " + "[WARN] : " + Text)


    def Error(Text:str):
        print()
        print(Colors.FAIL + Text + Colors.ENDC)
        File.WriteFile(CurrentLogFile, "(" + str(CurrentTime.hour) + "_" + str(CurrentTime.minute) + "_" + str(CurrentTime.second) + ")" + " -- " + "[ERROR] : " + Text)

    def Underline(Text:str):
        print()
        print(Colors.UNDERLINE + Text + Colors.ENDC)
        File.WriteFile(CurrentLogFile, "(" + str(CurrentTime.hour) + "_" + str(CurrentTime.minute) + "_" + str(CurrentTime.second) + ")" + " -- " + "[UNDERLINE] : " + Text)

    def Clear():
        cmd = 'clear'
        if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
            cmd = 'cls'
        os.system(cmd)
        File.WriteFile(CurrentLogFile, "(" + str(CurrentTime.hour) + "_" + str(CurrentTime.minute) + "_" + str(CurrentTime.second) + ")" + " -- " + "[CLEAR]" + "\n"*9 )    
#endregion

#region sys fichiers
class Directory:

    def GetCurrentDirectory():
        return os.path.dirname(os.path.realpath(__file__))

    def CreateDir(path = GetCurrentDirectory(), DirName:str = "ErrorNoName"):
        path = os.path.join(path, DirName)
        if Directory.Exist(path) == False:
            os.mkdir(path, 0o666)
        return path

    def Exist(path):
        return os.path.exists(path)

class File:

    def Exist(path):
        return os.path.exists(path)
    
    def CreateFile(path = Directory.GetCurrentDirectory(), FileName = "ErrorNoName", Extention = ".err"):
        path = os.path.join(path, FileName + Extention)
        if File.Exist(path) == False:
            tmp = open(path, 'w')
            tmp.close()
        return path

    def PathJoin(Path1, Path2):
        return os.path.join(Path1, Path2)
    
    def ReadText(FilePath):
        tmp = open(FilePath, 'r')
        Text = tmp.readlines()
        tmp.close()
        ToReturn = ""
        for ligne in Text:
            ToReturn += ligne.replace("\n","")
        return ToReturn
    
    def ReadLines(FilePath):
        tmp = open(FilePath, 'r')
        Text = tmp.readlines()
        tmp.close()
        ToReturn = ""
        for ligne in Text:
            ToReturn += ligne
        return ToReturn
    
    def WriteFile(FilePath, Text):
        currText = File.ReadLines(FilePath)
        tmp = open(FilePath, 'w')
        tmp.write(currText + Text + "\n")
        tmp.close()
#endregion

#region sys sauvegarde
class Load:
    def Str(Key:str):
        Debug.Log("Load str from " + Key)
        pass

    def Int(Key:str):
        Debug.Log("Load int from " + Key)
        pass

    def Float(Key:str):
        Debug.Log("Load float from " + Key)
        pass

    def Bool(Key:str):
        Debug.Log("Load bool from " + Key)
        pass

class Save:
    def __init__(self, Key:str, Value:vars) -> None:
        Debug.Log("Save data at " + Key)
        pass
        DataInSaveFile = File.ReadLines()
#endregion 

#region Le Jeu
class Game(arcade.Window):

    def __init__(self, Largeur, Longeur, Titre) -> None:
        super().__init__(Largeur, Longeur, Titre)
        Debug.Log("Game Init ...")
        self.set_icon(pyglet_load(icon_path))
        self.player_list = None
        self.physics_engine = None
        self.camera = None
        self.gui_camera = None
        self.Map = None
        self.MainSound = None
        self.CurrentBiome = "grass"
        self.IsPlaying = False
        self.MultiPlayersList = None
        self.AnimeFrame = 0

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        
        self.LargeurFenetre = Largeur
        self.LongeurFenetre = Longeur
        self.NomFenetre = Titre
        self.Gold = 0
        self.PlayerMaxHealth = 100
        self.PlayerHealth = 0
        self.PlayerDamage = 1
        self.Level = 0
        Debug.Log("Game Initialized !")

    def setup(self):
        Debug.Log("Game setting up ...")

        #region set vars
        self.player_list = arcade.SpriteList()
        self.MultiPlayersList = arcade.SpriteList()

        self.player_sprite = arcade.Sprite(PlayerSpriteDown, PlayerScale)
        self.player_sprite.center_x = 4300
        self.player_sprite.center_y = 4000
        self.AnimeFrame = 0

        self.player_list.append(self.player_sprite)
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)
        self.MainSound = arcade.load_sound(GrassMainAudio)

        self.Gold = 0
        self.PlayerMaxHealth = 100
        self.PlayerHealth = self.PlayerMaxHealth
        self.PlayerDamage = 1
        self.Level = 0

        self.enemy = Enemy(4300, 4000)
        self.enemy_list = arcade.SpriteList()
        self.enemy_list.append(self.enemy)
        #endregion

        layer_options = {
            "Ground": {
                "use_spatial_hash": True,
            },
            "Wall": {
                "use_spatial_hash": True,
            },
        }

        self.Map = arcade.load_tilemap(MapFilePath, TilesScale, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.Map)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, walls=self.scene["Wall"])

        try:
            Client.connect((ServerIP, ServerPort))
            TaskThread(self.ConnectToServer)
        except:
            Debug.Warn("No Server !")

    def process_keychange(self):
        if self.up_pressed == True:
            self.player_sprite.change_y = PlayerSpeed
            self.Player_Animation("up")
        elif self.down_pressed == True:
            self.player_sprite.change_y = -PlayerSpeed
            self.Player_Animation("down")
        else :
            self.player_sprite.change_y = 0

        if self.right_pressed == True:
            self.player_sprite.change_x = PlayerSpeed
            self.Player_Animation("right")
        elif self.left_pressed == True:
            self.player_sprite.change_x = -PlayerSpeed
            self.Player_Animation("left")
        else :
            self.player_sprite.change_x = 0

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.MultiPlayersList.draw()
        self.enemy.update()
        self.enemy_list.draw()
        self.player_list.draw()

        #region HUD
        self.gui_camera.use()
        guiPosY = self.LongeurFenetre - 20
        guiPosX = 10
        arcade.draw_rectangle_filled(self.LargeurFenetre // 2, self.LongeurFenetre - 14, self.LargeurFenetre, 24, arcade.color.BLACK)
        arcade.draw_text("Coins :  " + str(self.Gold), guiPosX, guiPosY, arcade.csscolor.WHITE, 24, font_name="Kenney Pixel")
        guiPosX += 150
        arcade.draw_text("Level :  " + str(self.Level), guiPosX, guiPosY, arcade.csscolor.WHITE, 24, font_name="Kenney Pixel")
        guiPosX += 150
        arcade.draw_text("Power :  " + str(self.PlayerDamage), guiPosX, guiPosY, arcade.csscolor.WHITE, 24, font_name="Kenney Pixel")
        guiPosX += 150
        arcade.draw_text("Health :  " + str(self.PlayerHealth) + " / " + str(self.PlayerMaxHealth), guiPosX, guiPosY, arcade.csscolor.WHITE, 24, font_name="Kenney Pixel")
        #endregion

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

    def Player_Animation(self, Direction:str):
        if Direction == "up":
            self.player_sprite.texture = arcade.load_texture(PlayerSpriteUp)
            self.AnimeFrame = 1
        elif Direction == "down":
            self.player_sprite.texture = arcade.load_texture(PlayerSpriteDown)
            self.AnimeFrame = 0
        elif Direction == "left":
            self.player_sprite.texture = arcade.load_texture(PlayerSpriteLeft)
            self.AnimeFrame = 2
        elif Direction == "right":
            self.player_sprite.texture = arcade.load_texture(PlayerSpriteRight)
            self.AnimeFrame = 3

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )
        
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def on_update(self, delta_time):
        
        self.physics_engine.update()
        self.center_camera_to_player()
        self.process_keychange()

        if self.CurrentBiome == "grass" and self.IsPlaying == False:
            arcade.play_sound(self.MainSound, 1, 0, True)
            self.IsPlaying = True

        SendData("&&PlayerPos=" + str(int(self.player_sprite.center_x)) + ";" + str(int(self.player_sprite.center_y)) + ";" + str(ClientIP))
        SendData("&&Animation=" + str(self.AnimeFrame) + ";" + str(ClientIP))

    def ConnectToServer(self):
        while True:
            try:
                ServerData = Client.recv(2048).decode('utf-8')
                AllData = ServerData.split('%')
                for Data in AllData:
                    if Data != "":
                        if Data.split('=')[0] == "&&PlayerPos":
                            if ClientIP != Data.split('=')[1].split(';')[2] and not(Data.split('=')[1].split(';')[2] in AllClient):
                                print(Data.split('=')[1].split(';')[0] + " __ " + Data.split('=')[1].split(';')[1])
                                AllClient[Data.split('=')[1].split(';')[2]] = arcade.Sprite(PlayerSpriteDown, PlayerScale)
                                AllClient[Data.split('=')[1].split(';')[2]].center_x = int(Data.split('=')[1].split(';')[0])
                                AllClient[Data.split('=')[1].split(';')[2]].center_y = int(Data.split('=')[1].split(';')[1])
                                self.MultiPlayersList.append(AllClient[Data.split('=')[1].split(';')[2]])

                            elif Data.split('=')[1].split(';')[2] in AllClient:
                                AllClient[Data.split('=')[1].split(';')[2]].center_x = int(Data.split('=')[1].split(';')[0])
                                AllClient[Data.split('=')[1].split(';')[2]].center_y = int(Data.split('=')[1].split(';')[1])

                        if Data.split('=')[0] == "&&Animation":
                            if ClientIP != Data.split('=')[1].split(';')[1] and Data.split('=')[1].split(';')[1] in AllClient:
                                print(Data.split('=')[1].split(';')[0])
                                if int(Data.split('=')[1].split(';')[0]) == 1:
                                    AllClient[Data.split('=')[1].split(';')[1]].texture = arcade.load_texture(PlayerSpriteUp)

                                if int(Data.split('=')[1].split(';')[0]) == 0:
                                    AllClient[Data.split('=')[1].split(';')[1]].texture = arcade.load_texture(PlayerSpriteDown)

                                if int(Data.split('=')[1].split(';')[0]) == 2:
                                    AllClient[Data.split('=')[1].split(';')[1]].texture = arcade.load_texture(PlayerSpriteLeft)

                                if int(Data.split('=')[1].split(';')[0]) == 3:
                                    AllClient[Data.split('=')[1].split(';')[1]].texture = arcade.load_texture(PlayerSpriteRight)

                    AllData = ""
            except Exception as er:
                print(er.args)

                """
                Client.close()
                break
                """

def IsConnectedToServer():
    if Run == False:
        return False
    try:
        SendData("&&")
        return True
    except Exception:
        return False
    return False


def StartFileVerification():
    """
    Gestionaire des fichier pour le jeu (sauvegarde et warn en cas de mauvaise instalation et/ou fichier manquant.)
    """

    ErrorCount = 0
    NumberOfTilesMaps = 62
    NumberOfCharactersSprites = 19
    NumberOfSwooshSprites = 5
    NumberOfWaterTiles = 3
    NumberOfGUISprites = 8

    TilesMapsFileName = "l0_sprite_"
    TileCharactersFileName = "sprite_"
    TileSwooshFileName = "Swoosh_"
    TileWaterFileName = "Water_"
    TileGUIFileName = "sprite_"

    RootPath = Directory.GetCurrentDirectory()

    if not(File.Exist(File.PathJoin(RootPath, "Saves"))):
        Debug.Log("Create Missing Folder : ")
        Debug.Underline(File.PathJoin(RootPath, "Saves"))
        Directory.CreateDir(RootPath, "Saves")

    if not(File.Exist(File.PathJoin(RootPath, "Graphics"))):
        Debug.Error("Missing Folder : ")
        Debug.Underline(File.PathJoin(RootPath, "Graphics"))
        ErrorCount += 1
    else :
        GraphicsPath = File.PathJoin(RootPath, "Graphics")

        if not(File.Exist(File.PathJoin(GraphicsPath, "TilesMap"))):
            Debug.Error("Missing Folder : ")
            Debug.Underline(File.PathJoin(GraphicsPath, "TilesMap"))
            ErrorCount += 1
        else :
            TilesMapPath = File.PathJoin(GraphicsPath, "TilesMap")
            for index in range(1, NumberOfTilesMaps):
                if not(File.Exist(File.PathJoin(TilesMapPath, TilesMapsFileName + str(index) + ".png"))):
                    Debug.Error("Missing Tile Map " + str(index) + " : ")
                    Debug.Underline(File.PathJoin(TilesMapPath, TilesMapsFileName + str(index) + ".png"))
                    ErrorCount += 1

        if not(File.Exist(File.PathJoin(GraphicsPath, "TilesCharacter"))):
            Debug.Error("Missing Folder : ")
            Debug.Underline(File.PathJoin(GraphicsPath, "TilesCharacter"))
            ErrorCount += 1
        else :
            TilesCharaterPath = File.PathJoin(GraphicsPath, "TilesCharacter")
            for index in range(1, NumberOfCharactersSprites):
                if not(File.Exist(File.PathJoin(TilesCharaterPath, TileCharactersFileName + str(index) + ".png"))):
                    Debug.Error("Missing Tile Map " + str(index) + " : ")
                    Debug.Underline(File.PathJoin(TilesCharaterPath, TileCharactersFileName + str(index) + ".png"))
                    ErrorCount += 1

        if not(File.Exist(File.PathJoin(GraphicsPath, "TileSwoosh"))):
            Debug.Error("Missing Folder : ")
            Debug.Underline(File.PathJoin(GraphicsPath, "TileSwoosh"))
            ErrorCount += 1
        else :
            TilesSwooshPath = File.PathJoin(GraphicsPath, "TileSwoosh")
            for index in range(NumberOfSwooshSprites):
                if not(File.Exist(File.PathJoin(TilesSwooshPath, TileSwooshFileName + str(index) + ".png"))):
                    Debug.Error("Missing Swoosh Tile " + str(index) + " : ")
                    Debug.Underline(File.PathJoin(TilesSwooshPath, TileSwooshFileName + str(index) + ".png"))
                    ErrorCount += 1

        if not(File.Exist(File.PathJoin(GraphicsPath, "TilesWater"))):
            Debug.Error("Missing Folder : ")
            Debug.Underline(File.PathJoin(GraphicsPath, "TilesWater"))
            ErrorCount += 1
        else :
            TilesWaterPath = File.PathJoin(GraphicsPath, "TilesWater")
            for index in range(NumberOfWaterTiles):
                if not(File.Exist(File.PathJoin(TilesWaterPath, TileWaterFileName + str(index) + ".png"))):
                    Debug.Error("Missing Water Tile " + str(index) + " : ")
                    Debug.Underline(File.PathJoin(TilesWaterPath, TileWaterFileName + str(index) + ".png"))
                    ErrorCount += 1

        if not(File.Exist(File.PathJoin(GraphicsPath, "TileGUI"))):
            Debug.Error("Missing Folder : ")
            Debug.Underline(File.PathJoin(GraphicsPath, "TileGUI"))
            ErrorCount += 1
        else :
            TilesGUIPath = File.PathJoin(GraphicsPath, "TileGUI")
            for index in range(NumberOfGUISprites):
                if not(File.Exist(File.PathJoin(TilesGUIPath, TileGUIFileName + str(index) + ".png"))):
                    Debug.Error("Missing GUI Sprites " + str(index) + " : ")
                    Debug.Underline(File.PathJoin(TilesGUIPath, TileGUIFileName + str(index) + ".png"))
                    ErrorCount += 1

    if not(File.Exist(File.PathJoin(RootPath, "Map.json"))):
        Debug.Error("Missing Map file : ")
        Debug.Underline(File.PathJoin(RootPath, "Map.json"))
        ErrorCount += 1

    if not(File.Exist(File.PathJoin(RootPath, "TilesMap.tsx"))):
        Debug.Error("Missing Tile Map Manager : ")
        Debug.Underline(File.PathJoin(RootPath, "TilesMap.tsx"))
        ErrorCount += 1

    if not(File.Exist(File.PathJoin(RootPath, "Audios"))):
        Debug.Error("Missing Folder : ")
        Debug.Underline(File.PathJoin(RootPath, "Audios"))
        ErrorCount += 1

    if not(File.Exist(File.PathJoin(RootPath, "ExecutionsLogs"))):
        Debug.Log("Create Missing Folder : ")
        Debug.Underline(File.PathJoin(RootPath, "Saves"))
        Directory.CreateDir(RootPath, "Saves")
        
    if ErrorCount == 0:
        Debug.Log("Files check : OK")
        return True
    
    Debug.Error("Can't launch App, Error At file Checking, Error Count : " + str(ErrorCount))
    return False

class Enemy(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(EnemiesSprite)
        self.center_x = x
        self.center_y = y

    def update(self):
        self.center_x -= EnemiesSpeed

def StartGame():
    FenetreDuJeu = Game(680, 440, "UnJeu")
    FenetreDuJeu.setup()
    Debug.Log("Running ...")
    arcade.run()
    Debug.Log("App closed !")
    sys.exit()
#endregion

def SendData(Data:str):
    try:
        Client.send(bytes("%" + Data, 'utf-8'))
    except:
        pass

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

#region Start script
try :
    FenetreDuJeu = None
    RootPath = Directory.GetCurrentDirectory()
    LogsPath = File.PathJoin(RootPath, "ExecutionsLogs")
    CurrentTime = datetime.datetime.now()
    CurrentLogFile = File.CreateFile(LogsPath, "Log_(" + str(CurrentTime.year) + "_" + str(CurrentTime.month) + "_" + str(CurrentTime.day) + ")__(" + str(CurrentTime.hour) + "_" + str(CurrentTime.minute) + "_" + str(CurrentTime.second) + ")" , ".txt")

    if StartFileVerification() == True:

        #region File Set :
        GraphicsPath = File.PathJoin(RootPath, "Graphics")
        SavesPath = File.PathJoin(RootPath, "Saves")
        AudiosPath = File.PathJoin(RootPath, "Audios")
        TilesMapPath = File.PathJoin(GraphicsPath, "TilesMap")
        TilesCharaterPath = File.PathJoin(GraphicsPath, "TilesCharacter")
        MapFilePath = File.PathJoin(RootPath, "Map.json")
        
        TilesSwooshPath = File.PathJoin(GraphicsPath, "TileSwoosh")
        TilesWaterPath = File.PathJoin(GraphicsPath, "TilesWater")
        TilesGUIPath = File.PathJoin(GraphicsPath, "TileGUI")
        icon_path = File.PathJoin(RootPath, "icon.ico")
        GrassMainAudio = File.PathJoin(AudiosPath, "TownTheme.mp3")

        PlayerSpriteDown = File.PathJoin(TilesCharaterPath, "sprite_6.png")
        PlayerAnimationDown1 = File.PathJoin(TilesCharaterPath, "sprite_7.png")
        PlayerAnimationDown2 = File.PathJoin(TilesCharaterPath, "sprite_8.png")

        PlayerSpriteUp = File.PathJoin(TilesCharaterPath, "sprite_9.png")
        PlayerAnimationUp1 = File.PathJoin(TilesCharaterPath, "sprite_10.png")
        PlayerAnimationUp2 = File.PathJoin(TilesCharaterPath, "sprite_11.png")

        PlayerSpriteRight = File.PathJoin(TilesCharaterPath, "sprite_12.png")
        PlayerAnimationRight1 = File.PathJoin(TilesCharaterPath, "sprite_13.png")
        PlayerAnimationRight2 = File.PathJoin(TilesCharaterPath, "sprite_14.png")

        PlayerSpriteLeft = File.PathJoin(TilesCharaterPath, "sprite_15.png")
        PlayerAnimationLeft1 = File.PathJoin(TilesCharaterPath, "sprite_16.png")
        PlayerAnimationLeft2 = File.PathJoin(TilesCharaterPath, "sprite_17.png")

        EnemiesSprite = File.PathJoin(TilesCharaterPath, "sprite_0.png")
        #endregion

        ServerIP = socket.gethostbyname(socket.gethostname())
        ServerIP = "172.29.10.18"
        ClientIP = get_ip_address()
        AllClient = dict()

        ServerPort = 7800
        Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Debug.Clear()

        # Vars :
        PlayerScale = 1
        PlayerSpeed = 5
        TilesScale = 1
        ObjectsScale = 1
        EnemiesSpeed = 2

        # Start Game
        Run = True
        Debug.Log("Launch App ...")
        StartGame()
        Run = False
except Exception as Error:
    Debug.Error(traceback.format_exc())
    sys.exit()

sys.exit()
#endregion