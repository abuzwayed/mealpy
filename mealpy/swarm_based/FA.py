#!/usr/bin/env python
# ------------------------------------------------------------------------------------------------------%
# Created by "Thieu Nguyen" at 22:07, 07/04/2020                                                        %
#                                                                                                       %
#       Email:      nguyenthieu2102@gmail.com                                                           %
#       Homepage:   https://www.researchgate.net/profile/Thieu_Nguyen6                                  %
#       Github:     https://github.com/thieunguyen5991                                                  %
#-------------------------------------------------------------------------------------------------------%

from numpy import abs, array, argmax, argmin, sum
from numpy.random import uniform, choice, randint, normal
from scipy.spatial.distance import cdist
from copy import deepcopy
from mealpy.root import Root


class BaseFA(Root):
    """
        The original version of: Fireworks Algorithm
            (Fireworks algorithm for optimization)
        Link:
            DOI: https://doi.org/10.1007/978-3-642-13495-1_44
    """

    def __init__(self, objective_func=None, problem_size=50, domain_range=(-1, 1), log=True, epoch=750, pop_size=100, m=50, a=0.04, b=0.8, A_=40, m_=5):
        Root.__init__(self, objective_func, problem_size, domain_range, log)
        self.epoch = epoch
        self.pop_size = pop_size            # n
        self.m = m                         # parameter controlling the total number of sparks generated by the pop_size fireworks
        self.a = a
        self.b = b
        self.A_ = A_
        self.m_ = m_

    def _train__(self):
        pop = [self._create_solution__() for _ in range(self.pop_size)]
        g_best = self._get_global_best__(pop=pop, id_fitness=self.ID_FIT, id_best=self.ID_MIN_PROB)

        for epoch in range(self.epoch):

            pop_new = []
            for i in range(0, self.pop_size):
                list_fit = array([item[self.ID_FIT] for item in pop])
                maxx_fit = pop[argmax(list_fit)][self.ID_FIT]
                minn_fit = pop[argmin(list_fit)][self.ID_FIT]
                si = self.m * (maxx_fit - pop[i][self.ID_FIT] + self.EPSILON) / (self.pop_size * maxx_fit - sum(list_fit) + self.EPSILON)
                Ai = self.A_ * (pop[i][self.ID_FIT] - minn_fit + self.EPSILON) / (sum(list_fit) - minn_fit + self.EPSILON)
                if si < self.a * self.m:
                    si_ = int(round(self.a * self.m) + 1)
                elif si > self.b * self.m:
                    si_ = int(round(self.b * self.m) + 1)
                else:
                    si_ = int(round(si) + 1)

                ## Algorithm 1
                for j in range(0, si_):
                    pos_new = deepcopy(pop[i][self.ID_POS])
                    z = round(uniform() * self.problem_size)
                    list_idx = choice(range(0, self.problem_size), z, replace=False)
                    displacement = Ai * uniform(-1, 1)
                    for k in range(0, z):
                        pos_new[list_idx[k]] += displacement
                        if pos_new[list_idx[k]] < self.domain_range[0] or pos_new[list_idx[k]] > self.domain_range[1]:
                            pos_new[list_idx[k]] = self.domain_range[0] + abs(pos_new[list_idx[k]]) % (self.domain_range[1] - self.domain_range[0])
                    fit = self._fitness_model__(pos_new)
                    pop_new.append([pos_new, fit])

            ## Algorithm 2
            for i in range(0, self.m_):
                idx = randint(0, self.pop_size)
                pos_new = deepcopy(pop[idx][self.ID_POS])
                z = round(uniform() * self.problem_size)
                list_idx = choice(range(0, self.problem_size), z, replace=False)
                displacement = normal(1, 1)             # Gaussian
                for j in range(0, z):
                    pos_new[list_idx[j]] += displacement
                    if pos_new[list_idx[j]] < self.domain_range[0] or pos_new[list_idx[j]] > self.domain_range[1]:
                        pos_new[list_idx[j]] = self.domain_range[0] + abs(pos_new[list_idx[j]]) % (self.domain_range[1] - self.domain_range[0])
                fit = self._fitness_model__(pos_new)
                pop_new.append([pos_new, fit])

            ## Update the global best
            pop.extend(pop_new)
            g_best = self._update_global_best__(pop, self.ID_MIN_PROB, g_best)
            self.loss_train.append(g_best[self.ID_FIT])
            if self.log:
                print("> Epoch: {}, Best fit: {}".format(epoch + 1, g_best[self.ID_FIT]))

            ## Select n-1 fireworks left, using density-based distance to make diversity of the population
            list_dist = []
            list_pos = array([item[self.ID_POS] for item in pop])
            for i in range(0, len(pop)):
                temp1 = cdist(list_pos[i].reshape(1, -1), list_pos)
                list_dist.append(sum(temp1.flatten()))
            pop_new = [(pop[i], list_dist[i]) for i in range(0, len(pop))]
            pop_new = sorted(pop_new, key=lambda item: item[1], reverse=True)
            pop = [pop_new[i][0] for i in range(0, self.pop_size-1)]
            pop.append(g_best)

        return g_best[self.ID_POS], g_best[self.ID_FIT], self.loss_train