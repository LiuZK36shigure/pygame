import pygame
import sys
import pygame.font
import pygame.gfxdraw
import numpy as np
pygame.init()   # 初始化
pygame.mixer.init()    # 初始化音频模块
sys.setrecursionlimit(100000) #递归深度
pygame.mixer.music.load('static\\voice\\纯音乐 - 梅花三弄 (古筝独奏版).mp3')
pygame.mixer.music.play(-1)

class GoGame:
    def __init__(self):
        self.gray = (210, 210, 210)    # 灰色
        self.white = (255, 255, 255)   # 白色
        self.black = (0, 0, 0)         # 黑色
        self.board = (220,175,91)      # 棋盘

        self.size = 780        # 棋盘尺寸
        self.screen = None     # 窗口
        self.player = True     # 玩家
        self.__font = None     # 字体
        self.black_score = 0   # 分数
        self.white_score = 0   # 分数

        self.current_move = False
        self.move_count = 0  # 记录落子次数，用于标号
        self.chessman = np.zeros((19, 19)) # 二维数组，存储棋盘状态
        self.chessman_number = np.zeros((19, 19), dtype=int)  # 记录每个棋子的数字标号

        self.drop_sound = pygame.mixer.Sound('./static/voice/drop_sound.wav')
        self.capture_sound = pygame.mixer.Sound('./static/voice/capture_sound.wav')
        self.mainback_ori = pygame.image.load('./static/picture/back.jpg')
        self.mainback = pygame.transform.scale(self.mainback_ori, (1080, 780))
        self.last_captured_position = None
    # 运行方法
    def run(self):
        self.screen = pygame.display.set_mode((self.size + 300, self.size))   # 打开窗口及尺寸
        pygame.display.set_caption('围棋游戏')   # 程序上方名字

        pygame.font.get_fonts()
        font_name = pygame.font.match_font('fangsong')  # 通用字体
        self.__font = pygame.font.Font(font_name, 25)

        self.main_menu()    # 显示主界面
        self.ChessBoard()   # 棋盘窗口
        self.panel()        # 控制板

        pygame.display.flip()   # 刷新屏幕
        clock = pygame.time.Clock()

        while True:
            clock.tick(60)   # 限制60fps
            for event in pygame.event.get():  # 后者是捕获操作，给前者事件
                if event.type == pygame.QUIT:   # 右上角关闭
                    sys.exit()
                elif event.type == pygame.MOUSEMOTION:  # 捕获鼠标移动事件
                    x, y = pygame.mouse.get_pos()
                    self.ChessBoard()  # 重新绘制棋盘
                    self.panel()  # 控制板
                    self.ShowChess()   # 显示所有棋子
                    self.show_preview(x, y)  # 显示预览
                    pygame.display.flip()     # 刷新屏幕
                elif event.type == pygame.MOUSEBUTTONDOWN:   # 鼠标点击获取坐标
                    x, y = pygame.mouse.get_pos()
                    if x <= self.size and y <= self.size:
                        if self.is_click_valid(x, y):         # 落子判断
                            if self.DownChess(x, y, self.player) : # 落子
                                self.ChangePlayer()                # 换玩家
                            self.ChessBoard()                  # 重新绘制棋盘
                            self.panel()                       # 控制板
                            self.ShowChess()                   # 显示所有棋子
                            pygame.display.flip()              # 刷新屏幕
                    else :
                        self.mouse(x,y)
                        self.ChessBoard()  # 重新绘制棋盘
                        self.panel()  # 控制板
                        self.ShowChess()  # 显示所有棋子
                        pygame.display.flip()  # 刷新屏幕


    # 主界面
    def main_menu(self):
        font_name = pygame.font.match_font('幼圆')           # 获得字体文件
        title_font = pygame.font.Font(font_name, 60)    # 定义字体
        button_font = pygame.font.Font(font_name, 40)

        title = title_font.render('围棋游戏', True, self.black)  # 写标题，搞按钮
        start_button = button_font.render('开始游戏', True, self.black)
        exit_button = button_font.render('结束游戏', True, self.black)

        title_rect = title.get_rect(center=(240, 200))  # 定位
        start_button_rect = start_button.get_rect(center=(240, 400))
        exit_button_rect = exit_button.get_rect(center=(240, 500))

        while True:
            self.screen.blit(self.mainback, (0, 0))  # 填充屏幕，显示标题按钮
            self.screen.blit(title, title_rect)
            self.screen.blit(start_button, start_button_rect)
            self.screen.blit(exit_button, exit_button_rect)
            pygame.display.flip()  # 刷新屏幕

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if start_button_rect.collidepoint(x, y):  # 鼠标点到开始按钮
                        return
                    elif exit_button_rect.collidepoint(x, y):  # 鼠标点到结束按钮
                        pygame.quit()
                        sys.exit()

    # 计算分数
    def calculate_territory(self):
        self.black_score = 0
        self.white_score = 0
        for i in range(19):
            for j in range(19):
                if self.chessman[i][j] == 1:
                    self.black_score += 1
                elif self.chessman[i][j] == -1:
                    self.white_score += 1
                elif self.chessman[i][j] == 0:
                    neighbors = [(i+dx, j+dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)] if 0 <= i+dx < 19 and 0 <= j+dy < 19]
                    neighbor_values = [self.chessman[x][y] for x, y in neighbors]
                
         
                    if len(set(neighbor_values)) == 1 and neighbor_values[0] != 0:
                        if neighbor_values[0] == 1:
                            self.black_score += 1
                        else:
                            self.white_score += 1
                    else:
                        territory, borders = self.get_territory(i, j)
                        if len(borders) == 1:
                            if list(borders)[0] == 1:
                                self.black_score += len(territory)
                            else:
                                self.white_score += len(territory)

    def get_territory(self, x, y):
        territory = set()
        borders = set()
        to_explore = [(x, y)]
        checked = set()  # 用于跟踪已经检查过的点

        while to_explore:
            x, y = to_explore.pop()
            territory.add((x, y))
            checked.add((x, y))

            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 19 and 0 <= ny < 19:
                    if self.chessman[nx][ny] == 0 and (nx, ny) not in checked:
                        to_explore.append((nx, ny))
                        checked.add((nx, ny))
                    elif self.chessman[nx][ny] != 0:
                        borders.add(self.chessman[nx][ny])
                elif (nx, ny) not in checked:  # 检查棋盘边缘
                    borders.add(0)  # 使用0表示棋盘边缘
        return territory, borders

    def show_winner(self, winner_text):
        winner_surface = pygame.Surface((600, 100))
        winner_surface.fill(self.white)

        self.__btn_winner = pygame.Rect((self.size // 2) - 300, (self.size // 2) - 50, 600, 100)
        self.screen.blit(winner_surface, self.__btn_winner)

        pygame.draw.rect(self.screen, self.gray, ((self.size // 2) - 300, (self.size // 2) - 50, 600, 100), 6)
        font_name = pygame.font.match_font('幼圆')  # 获得字体文件
        font = pygame.font.Font(font_name, 60)
        text = font.render(winner_text, True, self.black)
        textRect = text.get_rect()
        textRect.center = (self.size // 2, self.size // 2)
        self.screen.blit(text, textRect)

        # 添加 "返回主页面" 按钮
        button_font = pygame.font.Font(font_name, 40)
        button_text = button_font.render("返回主页面", True, self.black)
        button_rect = button_text.get_rect(center=(self.size // 2, self.size // 2 + 100))
        pygame.draw.rect(self.screen, self.gray, button_rect.inflate(20, 10))
        self.screen.blit(button_text, button_rect)
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if button_rect.collidepoint(x, y):
                        self.__init__()
                        self.run()

    # 换手
    def ChangePlayer(self):
        self.player = False if self.player else True

    # 落子
    def DownChess(self, x, y, player):
      rounded_x = round((x - 30) / 40) * 40 + 30
      rounded_y = round((y - 30) / 40) * 40 + 30

      if self.is_click_valid(rounded_x, rounded_y):
        temp_chessman = np.copy(self.chessman)
        temp_chessman[(rounded_x - 30) // 40][(rounded_y - 30) // 40] = 1 if player else -1

        capture_occurred = self.check_capture(rounded_x, rounded_y, player, temp_chessman)
        if capture_occurred:
            self.chessman = np.copy(temp_chessman)  # 更新棋盘状态

        if not self.is_suicide_move((rounded_x - 30) // 40, (rounded_y - 30) // 40, player, temp_chessman):
            self.chessman[(rounded_x - 30) // 40][(rounded_y - 30) // 40] = 1 if player else -1
            self.move_count += 1
            self.chessman_number[(rounded_x - 30) // 40][(rounded_y - 30) // 40] = self.move_count
            self.drop_sound.play()
            if not capture_occurred:
                self.last_captured_position = None  # 如果没有其他的棋子被吃掉，重置last_captured_position
            return True

      return False
    #落子合法
    def is_click_valid(self, x, y):
      grid_x, grid_y = self.get_closest_point(x, y)
      index_x = (grid_x - 30) // 40
      index_y = (grid_y - 30) // 40
      if 0 <= index_x < 19 and 0 <= index_y < 19:
        distance = np.sqrt((grid_x - x) ** 2 + (grid_y - y) ** 2)
        if distance < 15:
            if self.chessman[index_x][index_y] == 0:
                if (index_x, index_y) == self.last_captured_position:  # 检查是否试图在最后一个被吃掉的位置上落子
                    self.show_ko_warning()  # 显示打劫警告
                    return False
                return True
      return False

    #棋子显示
    def ShowChess(self):
        for i in range(len(self.chessman)):
            for j in range(len(self.chessman[i])):
                if self.chessman[i][j] != 0:
                    # 绘制棋子
                    color = self.black if self.chessman[i][j] == 1 else self.white
                    pygame.gfxdraw.aacircle(self.screen, 30 + 40 * i, 30 + 40 * j, 18, color)
                    pygame.gfxdraw.filled_circle(self.screen, 30 + 40 * i, 30 + 40 * j, 18, color)

                    # 绘制棋子上的数字
                    font = pygame.font.Font(None, 20)
                    text_color = self.white if self.chessman[i][j] == 1 else self.black
                    text = font.render(str(self.chessman_number[i][j]), True, text_color)
                    textRect = text.get_rect()
                    textRect.center = (30 + 40 * i, 30 + 40 * j)
                    self.screen.blit(text, textRect)
    #预落子
    def show_preview(self, x, y):
      if x <= self.size and y <= self.size:
        if self.is_click_valid(x, y):
            grid_x, grid_y = self.get_closest_point(x, y)
            color = self.black if self.player else self.white
            pygame.gfxdraw.aacircle(self.screen, grid_x, grid_y, 18, color)
            pygame.gfxdraw.filled_circle(self.screen, grid_x, grid_y, 18, (color[0], color[1], color[2], 128))  # 半透明

            temp_chessman = np.copy(self.chessman)
            temp_chessman[(grid_x - 30) // 40][(grid_y - 30) // 40] = 1 if self.player else -1
            for i in range(19):
                for j in range(19):
                    if temp_chessman[i][j] == (-1 if self.player else 1) and self.is_dead(i, j, set(), temp_chessman):
                        pygame.gfxdraw.aacircle(self.screen, 30 + 40 * i, 30 + 40 * j, 18, color)
                        pygame.gfxdraw.filled_circle(self.screen, 30 + 40 * i, 30 + 40 * j, 18, (color[0], color[1], color[2], 128))  # 半透明
    def check_capture(self, x, y, player, chessman_state):
      capture_occurred = False
      for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nx, ny = (x - 30) // 40 + dx, (y - 30) // 40 + dy
        if 0 <= nx < 19 and 0 <= ny < 19 and chessman_state[nx][ny] == (-1 if player else 1):
            if self.is_dead(nx, ny, set(), chessman_state):
                self.remove_group(nx, ny, chessman_state)
                capture_occurred = True
                self.capture_sound.play()
      return capture_occurred

    def is_dead(self, x, y, visited, chessman_state):
      if (x, y) in visited:
        return True

      visited.add((x, y))
      color = chessman_state[x][y]
      for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 19 and 0 <= ny < 19:
            if chessman_state[nx][ny] == 0:
                return False
            elif chessman_state[nx][ny] == color and not self.is_dead(nx, ny, visited, chessman_state):
                return False

      return True

    # 移除被吃的棋子
    def remove_group(self, x, y, chessman_state):
      color = chessman_state[x][y]
      chessman_state[x][y] = 0
      self.chessman_number[x][y] = 0
      self.last_captured_position = (x, y)  # 更新最后一个被吃掉的棋子的位置
      for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 19 and 0 <= ny < 19 and chessman_state[nx][ny] == color:
            self.remove_group(nx, ny, chessman_state)

    # 棋盘
    def ChessBoard(self):
        self.screen.fill(self.board)
        # 加入坐标轴
        for i in range(30, self.size + 10, 40):
            if i == 30 or i == 750:
                pygame.draw.line(self.screen, [0, 0, 0], [i, 30], [i, 750], 4)
                pygame.draw.line(self.screen, [0, 0, 0], [30, i], [750, i], 4)
            else:
                pygame.draw.line(self.screen, [0, 0, 0], [i, 30], [i, 750], 2)
                pygame.draw.line(self.screen, [0, 0, 0], [30, i], [750, i], 2)
        # 加入棋盘坐标
        for i in range(19):
            font = pygame.font.Font(None, 20)
            text = font.render(str(i + 1), True, self.black)
            textRect = text.get_rect()
            textRect.center = (15, i * 40 + 30)
            self.screen.blit(text, textRect)
            text = font.render(chr(i + 65), True, self.black)
            textRect = text.get_rect()
            textRect.center = (i * 40 + 30, 15)
            self.screen.blit(text, textRect)
        # 绘制星位点
        for x in [3, 9, 15]:
            for y in [3, 9, 15]:
                pygame.gfxdraw.aacircle(self.screen, 30 + x * 40, 30 + y * 40, 5, self.black)
                pygame.gfxdraw.filled_circle(self.screen, 30 + x * 40, 30 + y * 40, 5, self.black)

    # 自杀判定
    def is_suicide_move(self, x, y, player, temp_chessman):
      return self.is_dead(x, y, set(), temp_chessman)

    def get_closest_point(self, x, y):
       grid_x = round((x - 30) / 40) * 40 + 30
       grid_y = round((y - 30) / 40) * 40 + 30
       grid_x = max(30, min(grid_x, 750))
       grid_y = max(30, min(grid_y, 750))
       return grid_x, grid_y

    ## 右侧控制器
    def panel(self):
        self.btnNew(self.screen)
        self.btnAction(self.screen)
        self.show_player(self.screen)

    def btnNew(self, screen):
        # 重新开始
        new_surface = pygame.Surface((260, 50))
        new_surface.fill(self.white)

        self.__btn_new = pygame.Rect(self.size + 20, 20, 260, 50)
        screen.blit(new_surface, self.__btn_new)

        pygame.draw.rect(screen, self.gray, (self.size + 20, 20, 260, 50), 6)
        text = self.__font.render("重  新  开  始", True, self.black)

        textRect = text.get_rect()
        textRect.center = (self.size + 150, 45)
        screen.blit(text, textRect)

    def btnAction(self, screen):
        # 停一手
        pass_surface = pygame.Surface((260, 50))
        pass_surface.fill(self.white)

        self.__btn_pass = pygame.Rect(self.size + 20, 90, 260, 50)
        screen.blit(pass_surface, self.__btn_pass)

        text = self.__font.render("过 一 手", True, self.black)
        textRect = text.get_rect()

        textRect.center = (self.size + 150, 115)
        screen.blit(text, textRect)
        pygame.draw.rect(screen, self.gray, (self.size + 20, 90, 260, 50), 6)

        # 认输
        loss_surface = pygame.Surface((260, 50))
        loss_surface.fill(self.white)

        self.__btn_loss = pygame.Rect(self.size + 20, 160, 260, 50)
        screen.blit(loss_surface, self.__btn_loss)

        text = self.__font.render("认   输", True, self.black)
        textRect = text.get_rect()

        textRect.center = (self.size + 150, 185)
        screen.blit(text, textRect)
        pygame.draw.rect(screen, self.gray, (self.size + 20, 160, 260, 50), 6)

        # 游戏结束
        end_surface = pygame.Surface((260, 50))
        end_surface.fill(self.white)

        self.__btn_end = pygame.Rect(self.size + 20, 300, 260, 50)
        screen.blit(end_surface, self.__btn_end)

        text = self.__font.render("游  戏  结  束", True, self.black)
        textRect = text.get_rect()

        textRect.center = (self.size + 150, 325)
        screen.blit(text, textRect)
        pygame.draw.rect(screen, self.gray, (self.size + 20, 300, 260, 50), 6)

    def show_player(self, screen):
        pygame.font.get_fonts()
        font_name = pygame.font.match_font('fangsong')  # 通用字体
        font = pygame.font.Font(font_name, 35)
        pygame.draw.rect(screen, self.board , (self.size + 40, 670, 200, 10), 0)
        text = font.render("人 生 如 棋", True, self.black)
        textRect = text.get_rect()
        textRect.center = (self.size + 140, 620)
        screen.blit(text, textRect)

        pygame.draw.rect(screen, self.board , (self.size + 40, 675, 200, 10), 0)
        text = font.render("落 子 无 悔", True, self.black)
        textRect = text.get_rect()
        textRect.center = (self.size + 140, 655)
        screen.blit(text, textRect)

        pygame.draw.rect(screen, self.board , (self.size + 30, 700, 200, 10), 0)
        text = self.__font.render("当 前 落 子", True, self.black)
        textRect = text.get_rect()
        textRect.center = (self.size + 110, 725)
        screen.blit(text, textRect)

        if self.player:
            player_surface = pygame.Surface((50, 50))
            player_surface.fill(self.black)

            self.__btn_player = pygame.Rect(self.size + 210, 700, 50, 50)
            screen.blit(player_surface, self.__btn_player)

            pygame.draw.rect(screen, self.gray, (self.size + 210, 700, 50, 50), 5)
            text = self.__font.render("黑", True, self.white)

            textRect = text.get_rect()
            textRect.center = (self.size + 235, 725)
            screen.blit(text, textRect)

        else :
            player_surface = pygame.Surface((50, 50))
            player_surface.fill(self.white)

            self.__btn_player = pygame.Rect(self.size + 210, 700, 50, 50)
            screen.blit(player_surface, self.__btn_player)

            pygame.draw.rect(screen, self.gray, (self.size + 210, 700, 50, 50), 5)
            text = self.__font.render("白", True, self.black)

            textRect = text.get_rect()
            textRect.center = (self.size + 235, 725)
            screen.blit(text, textRect)

    def show_ko_warning(self):
      font_name = pygame.font.match_font('fangsong')  # 通用字体
      font = pygame.font.Font(font_name, 35)
      text = font.render("打劫了，请在别处落子", True, self.black)
      textRect = text.get_rect()
      textRect.center = (self.size + 150, 400)
      self.screen.blit(text, textRect)
      pygame.display.flip()
      pygame.time.wait(1000)  # 显示警告1.5秒
    def mouse(self,x,y):
        p = (x,y)
        new = pygame.Rect.collidepoint(self.__btn_new, p)
        btn_pass = pygame.Rect.collidepoint(self.__btn_pass, p)
        btn_loss = pygame.Rect.collidepoint(self.__btn_loss, p)
        btn_end = pygame.Rect.collidepoint(self.__btn_end, p)
        if new:
            self.player = True
            self.chessman = np.zeros((19, 19))
            self.move_count = 0

        elif btn_pass:
            self.ChangePlayer()

        elif btn_loss:
            if self.player:
                self.show_winner("白方胜利")
            else:
                self.show_winner("黑方胜利")
        
        elif btn_end:
            self.calculate_territory()  
            if self.black_score - 3.75 > self.white_score:
                self.show_winner("黑方胜利")
            else:
                self.show_winner("白方胜利")

        else:
            True

game = GoGame()
game.run()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.display.flip()

pygame.mixer.music.stop()
pygame.quit()

#                            _ooOoo_
#                           o8888888o
#                           88" . "88
#                           (| -_- |)
#                           O\  =  /O
#                        ____/`---'\____
#                      .'  \\|     |//  `.
#                     /  \\|||  :  |||//  \
#                    /  _||||| -:- |||||-  \
#                    |   | \\\  -  /// |   |
#                    | \_|  ''\---/''  |   |
#                    \  .-\__  `-`  ___/-. /
#                  ___`. .'  /--.--\  `. . __
#               ."" '<  `.___\_<|>_/___.'  >'"".
#              | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#              \  \ `-.   \_ __\ /__ _/   .-` /  /
#         ======`-.____`-.___\_____/___.-`____.-'======
#                            `=---='
#        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                      Buddha Bless, No Bug !
