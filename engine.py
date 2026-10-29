"""双矢棋 · 纯规则引擎（零依赖，逐格实现，便于逐行核对）

坐标系：board 是长度 144 的列表，下标 x = r*12 + c。
board[x] == 0 表示空格；1~6 表示该格有一颗棋子，值 = 落法编号 + 1。
落法（OPTIONS）是"两个方向"的组合，方向编号：0 上 / 1 右 / 2 下 / 3 左。
棋盘是环面：上下相连、左右相连。
"""

N = 12
CELLS = N * N

# 6 种棋子 = 从 4 个方向里任选 2 个
OPTIONS = [
    (1, 3),   # 右 + 左
    (0, 2),   # 上 + 下
    (0, 3),   # 上 + 左
    (0, 1),   # 上 + 右
    (1, 2),   # 下 + 右
    (2, 3),   # 下 + 左
]
DIRS = [(-1, 0), (0, 1), (1, 0), (0, -1)]   # 与方向编号一致


def wrap(v):
    return v % N


def initial_board():
    """开局：中央 2×2 四颗棋子，各指斜外侧"""
    b = [0] * CELLS
    b[5 * N + 5] = 3   # 上 + 左
    b[5 * N + 6] = 4   # 上 + 右
    b[6 * N + 5] = 6   # 下 + 左
    b[6 * N + 6] = 5   # 下 + 右
    return b


def pointed_dirs(board, x):
    """返回"有哪些方向的邻居正指着 x 这一格"。"""
    r, c = divmod(x, N)
    out = []
    for d, (dr, dc) in enumerate(DIRS):
        y = wrap(r + dr) * N + wrap(c + dc)
        v = board[y]
        # y 在 x 的 d 方向上；它要指向 x，就得包含方向 (d+2)%4
        if v and ((d + 2) % 4) in OPTIONS[v - 1]:
            out.append(d)
    return out


def legal_options(board, x):
    """规则②：新棋子的两个箭头不能指向那些正指着 x 的邻子。"""
    p = pointed_dirs(board, x)
    if not p:                     # 规则①：没有任何棋子指着它 → 不能落
        return []
    return [i for i, o in enumerate(OPTIONS) if o[0] not in p and o[1] not in p]


def legal_moves(board):
    """所有合法落点，返回 [(x, option_index), ...]"""
    out = []
    for x in range(CELLS):
        if board[x]:
            continue
        for i in legal_options(board, x):
            out.append((x, i))
    return out


def play(board, x, option_index):
    """落子（就地修改）"""
    board[x] = option_index + 1


def analyze(board):
    """四类格判定。

    返回 (kind, dead, sleep, playable)：
      kind[x] 取值 'occ' / 'play' / 'sleep' / 'dead'
      play : 被 1~2 个方向指着，现在就能落
      dead : 被 3 个及以上方向指着；或 k=0 且所在空区里没有任何可落格
      sleep: k=0，但所在空区里还有可落格（将来可能被激活）

    "空区"= 把棋子、以及上面第一类死格当墙，剩下的空格按上下左右连成的区域。
    """
    k = [0] * CELLS
    kind = ['occ' if board[x] else 'sleep' for x in range(CELLS)]
    for x in range(CELLS):
        if board[x]:
            continue
        k[x] = len(pointed_dirs(board, x))
        kind[x] = 'play' if 1 <= k[x] <= 2 else ('dead' if k[x] >= 3 else 'sleep')

    seen = [False] * CELLS
    for start in range(CELLS):
        if board[start] or k[start] >= 3 or seen[start]:
            continue
        stack = [start]
        seen[start] = True
        cells, has_play = [], False
        while stack:
            x = stack.pop()
            cells.append(x)
            if k[x] >= 1:
                has_play = True
            r, c = divmod(x, N)
            for dr, dc in DIRS:
                y = wrap(r + dr) * N + wrap(c + dc)
                if board[y] or k[y] >= 3 or seen[y]:
                    continue
                seen[y] = True
                stack.append(y)
        if not has_play:               # 整片空区没有可落格 → 全判死
            for x in cells:
                if k[x] == 0:
                    kind[x] = 'dead'

    return (kind,
            sum(1 for t in kind if t == 'dead'),
            sum(1 for t in kind if t == 'sleep'),
            sum(1 for t in kind if t == 'play'))


if __name__ == "__main__":
    b = initial_board()
    mv = legal_moves(b)
    kind, dead, sleep, play = analyze(b)
    print("开局合法落点：%d 个（%d 个格 × 平均 %.2f 种落法）"
          % (len(mv), len({x for x, _ in mv}),
             len(mv) / max(len({x for x, _ in mv}), 1)))
    print("四类格：可落 %d / 眠 %d / 死 %d / 已占 4" % (play, sleep, dead))
    print("首手示例：", mv[:5])
