from __future__ import division

import numpy as np

from .. import grad_descent_shared as shared
from ...parameters import val_default

def compute_score(g, traj, goal, beta, cached_P=None, debug=False,
        val_mod=val_default):
    assert len(traj) > 0, traj
    if cached_P is None:
        P = val_mod.action_probabilities(g, goal, beta=beta)
    else:
        P = cached_P

    # XXX: Keeping here for now, since it is useful for debugging, and I was
    #   recently confused by some beta MLE results.
    # A = g.Actions
    # s, a = traj[0]
    # V = val_mod.forwards_value_iter(g, goal)
    # Q = val_mod.q_values(g, goal)
    # import pdb; pdb.set_trace()

    score = np.zeros(len(traj))
    for i, (s, a) in enumerate(traj):
        score[i] = P[s, a]

    log_score = np.log(score, out=score)
    return np.sum(log_score)

def compute_grad(g, traj, goal, beta, debug=False, val_mod=val_default):
    assert len(traj) > 0, traj
    Q = val_mod.q_values(g, goal)
    # Prevent -inf * 0 in the multiply(P,Q) operation.
    # REQUIRES NUMPY VERSION 1.13
    np.nan_to_num(Q, copy=False)
    P = val_mod.action_probabilities(g, goal, beta=beta)
    assert Q.shape == P.shape

    q_sum = 0
    ex_q = np.multiply(P, Q)
    ex_q_sum = 0

    for s, a in traj:
        q_sum += Q[s, a]
        ex_q_sum += np.sum(ex_q[s])

    return -(1/beta/beta) * (q_sum - ex_q_sum)

def simple_search(g, traj, goal, *args, **kwargs):
    kwargs["compute_score"] = compute_score
    return shared.simple_search(g, traj, goal, *args, **kwargs)

def binary_search(g, traj, goal, *args, **kwargs):
    kwargs["compute_grad"] = compute_grad
    return shared.binary_search(g, traj, goal, *args, **kwargs)

def gradient_ascent(g, traj, goal, *args, **kwargs):
    kwargs["compute_score"] = compute_score
    kwargs["compute_grad"] = compute_grad
    return shared.gradient_ascent(g, traj, goal, *args, **kwargs)

def _main():
    from ...mdp import GridWorldMDP
    from ...util import display, build_traj_from_actions
    N = 5
    init = 0
    goal = N*N-1
    R = -1
    g = GridWorldMDP(N, N, default_reward=R)
    A = [g.Actions.UP, g.Actions.RIGHT, g.Actions.UP_RIGHT]

    for a1 in A:
        for a2 in A:
            print "=================="
            traj = build_traj_from_actions(g, init, (a1, a2))
            display(g, traj, init, goal)
            # print("simple search")
            # simple_search(g, traj, goal, verbose=True, min_beta=0.1, max_beta=10000)
            print("binary search")
            binary_search(g, traj, goal, verbose=True, min_beta=0.1, max_beta=10000)

if __name__ == '__main__':
    _main()
