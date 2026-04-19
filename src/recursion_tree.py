"""
Sum of Subsets — Backtracking Recursion Tree
Format: Binary Include / Exclude decision tree matching the reference image.

Each node shows:
  Row 1 │ Arr    : all array elements as coloured cells; current element
        │          highlighted in amber with a ✦ marker above
  Row 2 │ Subset : elements included so far (blue cells; empty box if none)
  Row 3 │ TargetSum = X  (X = TARGET - cur_sum; remaining amount needed)

Edge labels: "Not Include arr[d]" (left)  /  "Include arr[d]" (right)

Node colours
  Normal   → white bg, soft gray border
  Solution → white bg, thick GREEN dashed border   (TargetSum = 0)
  Dead end → very light pink bg, gray border       (leaf, TargetSum ≠ 0)
  Pruned   → soft red bg, red border               (cur_sum > TARGET)
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
from collections import defaultdict
import os

# ─────────────────────────────────────────────────────────────────────────────
# INPUT
# ─────────────────────────────────────────────────────────────────────────────
default_set = [3, 1, 2, 5, 4]
default_target = 5

raw_line = input("Enter set elements (space-separated integers): ").strip()
if raw_line:
    try:
        RAW_SET = [int(x) for x in raw_line.split()]
    except ValueError:
        print("Invalid set input. Using default set [3, 1, 2, 5, 4].")
        RAW_SET = default_set
else:
    RAW_SET = default_set

target_line = input("Enter target sum: ").strip()
if target_line:
    try:
        TARGET = int(target_line)
    except ValueError:
        print("Invalid target. Using default target 5.")
        TARGET = default_target
else:
    TARGET = default_target

if not RAW_SET:
    print("Empty set entered. Using default set [3, 1, 2, 5, 4].")
    RAW_SET = default_set

arr = sorted(RAW_SET)
n = len(arr)

print(f"  Sorted array : {arr}")
print(f"  Target       : {TARGET}")
print()

# ─────────────────────────────────────────────────────────────────────────────
# 1.  BUILD TREE
#
#  Node at depth d:
#    subset    = elements included by decisions 0 … d-1  (BEFORE deciding arr[d])
#    cur_sum   = sum(subset)
#    target_rem = TARGET - cur_sum
#    arr[d] is the element being decided NEXT  (highlighted in the Arr row)
#
#  Children (added in order [exclude, include] so left < right in layout):
#    Exclude arr[d]  →  same subset / sum, depth d+1
#    Include arr[d]  →  subset + arr[d], sum + arr[d], depth d+1
#
#  Termination rules:
#    • target_rem == 0           → 'solution'  (stop expanding; already at target)
#    • cur_sum  > TARGET         → 'pruned'    (over-sum; shouldn't reach target)
#    • depth    == n, rem ≠ 0   → 'dead'      (exhausted all elements, no match)
# ─────────────────────────────────────────────────────────────────────────────

node_ctr  = [0]
all_nodes = {}          # nid → dict
all_edges = []          # (parent_id, child_id, 'include'|'exclude')


def add_node(depth, subset, cur_sum, state, parent_id, choice=""):
    nid = node_ctr[0]; node_ctr[0] += 1
    all_nodes[nid] = dict(
        depth      = depth,
        subset     = list(subset),
        cur_sum    = cur_sum,
        target_rem = TARGET - cur_sum,
        state      = state,
        parent     = parent_id,
        choice     = choice,
    )
    if parent_id is not None:
        all_edges.append((parent_id, nid, choice))
    return nid


def build(parent_id, depth, subset, cur_sum):
    """Recursively create left (exclude) and right (include) children."""
    if depth >= n:
        return          # parent is already a leaf; nothing more to expand

    # ── LEFT child : exclude arr[depth] ──────────────────────────────────────
    ex_sum = cur_sum
    ex_sub = list(subset)
    ex_rem = TARGET - ex_sum
    if ex_rem == 0:
        ex_state = 'solution'               # already at target without this elem
    elif depth + 1 == n:
        ex_state = 'dead'                   # no more elements; didn't reach target
    else:
        ex_state = 'normal'

    cid_ex = add_node(depth + 1, ex_sub, ex_sum, ex_state, parent_id, 'exclude')
    if ex_state == 'normal':
        build(cid_ex, depth + 1, ex_sub, ex_sum)

    # ── RIGHT child : include arr[depth] ─────────────────────────────────────
    in_sum = cur_sum + arr[depth]
    in_sub = list(subset) + [arr[depth]]
    in_rem = TARGET - in_sum
    if in_sum > TARGET:
        in_state = 'pruned'                 # over-sum → cut branch
    elif in_rem == 0:
        in_state = 'solution'               # exact match!
    elif depth + 1 == n:
        in_state = 'dead'                   # all elements used; not reached target
    else:
        in_state = 'normal'

    cid_in = add_node(depth + 1, in_sub, in_sum, in_state, parent_id, 'include')
    if in_state == 'normal':
        build(cid_in, depth + 1, in_sub, in_sum)


# Root: depth 0, empty subset, deciding arr[0]
root_id = add_node(0, [], 0, 'normal', None, "")
build(root_id, 0, [], 0)

sol_cnt   = sum(1 for d in all_nodes.values() if d['state'] == 'solution')
dead_cnt  = sum(1 for d in all_nodes.values() if d['state'] == 'dead')
prune_cnt = sum(1 for d in all_nodes.values() if d['state'] == 'pruned')

print(f"  Total nodes  : {len(all_nodes)}")
print(f"  Solutions    : {sol_cnt}")
print(f"  Dead ends    : {dead_cnt}")
print(f"  Pruned       : {prune_cnt}")
print()

# ─────────────────────────────────────────────────────────────────────────────
# 2.  LAYOUT  (leaf-cursor algorithm — same as N-Queens reference)
# ─────────────────────────────────────────────────────────────────────────────

children = defaultdict(list)
for (pid, cid, ch) in all_edges:
    children[pid].append(cid)          # order: exclude first → "left" child

# Visual dimensions
NODE_W = 3.40     # node box width
NODE_H = 1.60     # node box height
H_GAP  = 0.60     # horizontal gap between same-level leaf nodes
V_GAP  = 1.70     # vertical gap between depth levels (room for edge labels)

pos      = {}
x_cursor = [0.0]


def layout(nid, depth):
    ch = children.get(nid, [])
    if not ch:                                    # leaf → place at cursor
        cx = x_cursor[0] + NODE_W / 2
        cy = -depth * (NODE_H + V_GAP)
        pos[nid] = (cx, cy)
        x_cursor[0] += NODE_W + H_GAP
        return
    for child in ch:
        layout(child, depth + 1)
    cxs = [pos[c][0] for c in ch]
    pos[nid] = (
        (min(cxs) + max(cxs)) / 2.0,
        -depth * (NODE_H + V_GAP),
    )


layout(root_id, 0)

all_xs = [v[0] for v in pos.values()]
all_ys = [v[1] for v in pos.values()]

# ─────────────────────────────────────────────────────────────────────────────
# 3.  COLOUR SCHEME
# ─────────────────────────────────────────────────────────────────────────────

STATE_STYLE = {
    'normal'  : dict(bg='#FFFFFF', ec='#90A4AE', lw=1.4, ls='-' ),
    'solution': dict(bg='#FFFFFF', ec='#2E7D32', lw=2.4, ls='--'),
    'dead'    : dict(bg='#FFF5F5', ec='#BDBDBD', lw=1.2, ls='-' ),
    'pruned'  : dict(bg='#FFF3F3', ec='#EF5350', lw=1.8, ls='-' ),
}

# ─────────────────────────────────────────────────────────────────────────────
# 4.  FIGURE
# ─────────────────────────────────────────────────────────────────────────────

FIG_W = (max(all_xs) - min(all_xs)) + NODE_W + 8.5
FIG_H = abs(min(all_ys)) + NODE_H + 5.0

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')
ax.set_aspect('equal')
ax.axis('off')

# ── Edges + edge labels ───────────────────────────────────────────────────────
for (pid, cid, choice) in all_edges:
    px, py = pos[pid]
    cx, cy = pos[cid]
    d = all_nodes[pid]['depth']

    ec    = '#43A047' if choice == 'include' else '#90A4AE'
    lc    = '#1B5E20' if choice == 'include' else '#455A64'
    label = f"Include a[{d}]" if choice == 'include' else f"Exclude a[{d}]"

    ax.plot([px, cx], [py - NODE_H/2, cy + NODE_H/2],
            color=ec, linewidth=1.35, zorder=1)

    mx = (px + cx) / 2
    my = (py - NODE_H/2 + cy + NODE_H/2) / 2
    ax.text(mx, my, label,
            ha='center', va='center', fontsize=10.0, color=lc, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.14', fc='#FFFFFF', ec='#CFD8DC', alpha=0.96),
            zorder=3)

# ─────────────────────────────────────────────────────────────────────────────
# 5.  NODE DRAWING FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

# Internal layout constants (computed once)
CELL   = 0.31     # square cell side for element boxes
GAP    = 0.05     # gap between cells
PADL   = 0.14     # left inner padding
PADT   = 0.12     # top  inner padding
LBLW   = 0.92     # width reserved for "Arr" / "Subset" label
ROWSP  = 0.46     # vertical spacing between rows
DIVLW  = 0.5      # divider line weight


def draw_node(cx, cy, node):
    state  = node['state']
    depth  = node['depth']
    subset = node['subset']
    rem    = node['target_rem']
    s      = STATE_STYLE[state]

    x0 = cx - NODE_W / 2
    y0 = cy - NODE_H / 2

    # ── Node box (background + border) ───────────────────────────────────────
    ax.add_patch(Rectangle(
        (x0, y0), NODE_W, NODE_H,
        facecolor=s['bg'], edgecolor=s['ec'],
        linewidth=s['lw'], linestyle=s['ls'],
        zorder=4
    ))

    # ── Row y-positions (top edges of each row) ───────────────────────────────
    r1_y = y0 + NODE_H - PADT - CELL      # Arr row
    r2_y = r1_y - ROWSP                   # Subset row
    r3_y = r2_y - ROWSP * 0.82            # TargetSum text

    # ─── ROW 1 : Arr ─────────────────────────────────────────────────────────
    ax.text(x0 + PADL, r1_y + CELL / 2, "Arr",
            ha='left', va='center', fontsize=13.0,
            color='#37474F', fontweight='bold', zorder=6)

    for j in range(n):
        bx      = x0 + PADL + LBLW + j * (CELL + GAP)
        is_cur  = (j == depth) and (depth < n)
        is_incl = arr[j] in subset        # works because arr has distinct values

        if is_cur:
            fc, ec_c = '#FFD54F', '#E65100'    # amber  = current decision
        elif is_incl:
            fc, ec_c = '#BBDEFB', '#1565C0'    # blue   = already included
        else:
            fc, ec_c = '#FFF9C4', '#F9A825'    # yellow = not yet decided

        ax.add_patch(Rectangle(
            (bx, r1_y), CELL, CELL,
            facecolor=fc, edgecolor=ec_c,
            linewidth=0.75, zorder=5
        ))
        ax.text(bx + CELL / 2, r1_y + CELL / 2, str(arr[j]),
                ha='center', va='center',
                fontsize=11.0, color='#212121', fontweight='bold', zorder=6)

        # ✦ marker above current element
        if is_cur:
            ax.text(bx + CELL / 2, r1_y + CELL + 0.018, '✦',
                    ha='center', va='bottom',
                    fontsize=10.0, color='#E65100', zorder=6)

    # Divider line
    ax.plot([x0 + 0.06, x0 + NODE_W - 0.06],
            [r2_y + CELL + 0.028, r2_y + CELL + 0.028],
            color='#ECEFF1', lw=DIVLW, zorder=5)

    # ─── ROW 2 : Subset ──────────────────────────────────────────────────────
    ax.text(x0 + PADL, r2_y + CELL / 2, "Subset",
            ha='left', va='center', fontsize=12.0,
            color='#37474F', fontweight='bold', zorder=6)

    sub_x0 = x0 + PADL + LBLW
    if not subset:
        # Empty subset → one empty placeholder box
        ax.add_patch(Rectangle(
            (sub_x0, r2_y), CELL, CELL,
            facecolor='#F5F5F5', edgecolor='#BDBDBD',
            linewidth=0.75, zorder=5
        ))
    else:
        for j, elem in enumerate(subset):
            bx = sub_x0 + j * (CELL + GAP)
            ax.add_patch(Rectangle(
                (bx, r2_y), CELL, CELL,
                facecolor='#E3F2FD', edgecolor='#1E88E5',
                linewidth=0.75, zorder=5
            ))
            ax.text(bx + CELL / 2, r2_y + CELL / 2, str(elem),
                    ha='center', va='center',
                    fontsize=11.0, color='#0D47A1', fontweight='bold', zorder=6)

    # Divider line
    ax.plot([x0 + 0.06, x0 + NODE_W - 0.06],
            [r3_y + CELL * 0.9 + 0.026, r3_y + CELL * 0.9 + 0.026],
            color='#ECEFF1', lw=DIVLW, zorder=5)

    # ─── ROW 3 : TargetSum ───────────────────────────────────────────────────
    if rem == 0:
        ts_col, ts_fw = '#2E7D32', 'bold'
    elif rem < 0:
        ts_col, ts_fw = '#C62828', 'bold'
    else:
        ts_col, ts_fw = '#455A64', 'normal'

    ax.text(x0 + PADL, r3_y + CELL * 0.45,
            f"TargetSum = {rem}",
            ha='left', va='center',
            fontsize=12.0, color=ts_col, fontweight=ts_fw, zorder=6)


# Draw every node
for nid, data in all_nodes.items():
    draw_node(*pos[nid], data)

# ─────────────────────────────────────────────────────────────────────────────
# 6.  LEGEND
# ─────────────────────────────────────────────────────────────────────────────

leg_x     = max(all_xs) + NODE_W / 2 + 0.55
leg_y_top = max(all_ys) + NODE_H / 2
LBOX, LPAD = 0.42, 0.78

legend_items = [
    ('normal',   'Normal node'),
    ('solution', 'Solution  (TargetSum = 0)'),
    ('dead',     'Dead-end leaf'),
    ('pruned',   'Pruned  (cur_sum > Target)'),
]

ax.add_patch(FancyBboxPatch(
    (leg_x - 0.18, leg_y_top - len(legend_items) * LPAD - 0.20),
    3.6, len(legend_items) * LPAD + 0.52,
    boxstyle='round,pad=0.05',
    facecolor='#FAFAFA', edgecolor='#CFD8DC',
    linewidth=1.0, zorder=7
))

for i, (st, lbl) in enumerate(legend_items):
    s  = STATE_STYLE[st]
    bx = leg_x
    by = leg_y_top - i * LPAD
    ax.add_patch(Rectangle(
        (bx, by - LBOX + 0.04), LBOX, LBOX,
        facecolor=s['bg'], edgecolor=s['ec'],
        linewidth=s['lw'], linestyle=s['ls'], zorder=8
    ))
    ax.text(bx + LBOX + 0.16, by - LBOX / 2 + 0.04,
            lbl, fontsize=13.0, va='center', color='#37474F', zorder=8)

# ─────────────────────────────────────────────────────────────────────────────
# 7.  TITLE + STATS
# ─────────────────────────────────────────────────────────────────────────────

cx_t = (min(all_xs) + max(all_xs)) / 2

ax.text(cx_t, max(all_ys) + NODE_H / 2 + 0.75,
        'Sum of Subsets  —  Backtracking Recursion Tree',
        ha='center', fontsize=24, fontweight='bold', color='#1A237E', zorder=9)

ax.text(cx_t, max(all_ys) + NODE_H / 2 + 0.42,
        f'Set = {arr}   │   Target = {TARGET}',
        ha='center', fontsize=16, color='#37474F', zorder=9)

ax.text(cx_t, max(all_ys) + NODE_H / 2 + 0.15,
        f'Total nodes: {len(all_nodes)}  ·  '
        f'Solutions: {sol_cnt}  ·  '
        f'Dead ends: {dead_cnt}  ·  '
        f'Pruned: {prune_cnt}',
        ha='center', fontsize=14, color='#90A4AE', zorder=9)

# ─────────────────────────────────────────────────────────────────────────────
# 8.  SAVE
# ─────────────────────────────────────────────────────────────────────────────

ax.set_xlim(min(all_xs) - NODE_W - 0.3, leg_x + 4.0)
ax.set_ylim(min(all_ys) - NODE_H - 0.5, max(all_ys) + NODE_H + 1.6)

plt.tight_layout(pad=0.3)

out_dir  = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "recursion_tree.png")

plt.savefig(out_path, dpi=360, bbox_inches='tight', facecolor='#FFFFFF')
print(f"  Saved: {os.path.abspath(out_path)}")
plt.close()
