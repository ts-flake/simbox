# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/03b_examples.chemistry.ipynb.

# %% auto 0
__all__ = ['draw_ellipse', 'CSTR']

# %% ../../nbs/03b_examples.chemistry.ipynb 3
import warnings
from ..basics import *

# %% ../../nbs/03b_examples.chemistry.ipynb 5
def draw_ellipse(ax=None, center=[0,0], A=np.eye(2), rho=1, color='b', figsize=(3,3)):
    "Draw an ellipse defined by a positive-definite matrix `A` and squared radius `rho`."
    if ax is None: fig,ax = plt.subplots(figsize=figsize)
    l = np.linspace(0,2*np.pi,100)
    pts = np.vstack([np.cos(l), np.sin(l)]) * np.sqrt(rho)
    pts = pts.T @ np.linalg.inv(np.linalg.cholesky(A)) + center
    ax.plot(*pts.T, '-', c=color)

# %% ../../nbs/03b_examples.chemistry.ipynb 9
class CSTR(ParamsMixin, LeafSystem):
    "Continuous Stirred Tank Reactor."
    named_inp    = namedview('input', ('C_A0','Q'))
    named_state  = namedview('state', ('C_A','T'))
    named_params = namedview('params', ('k0','rho_L','C_p','R','E','F','T0','V','dH'))
    _param_units = ('m^3/kmol/hr', 'kg/m^3', 'kJ/kg/K', 'kJ/kmol/K', 'kJ/kmol', 'm^3/hr', 'K', 'm^3', 'kJ/kmol')
    def __init__(self, set_params_mannually: bool=False, params: Union[list[float], np.ndarray]=None):
        super().__init__()
        self.set_name('CSTR')
        self._numeric_params = BasicVector([8.46e6, 1000., .231, 8.314, 5e4, 5., 300., 1., -1.15e4]) # Default values
        state = self.DeclareContinuousState(2)
        self.DeclareVectorInputPort(name='u', size=2)
        self.DeclareStateOutputPort('y=x', state)
        if set_params_mannually: self._update_params() # Set parameter values mannually
        if params is not None and not set_params_mannually: # Set parameter values from a vector
            assert len(params) == len(self._param_units), f"Expect `params` of length {len(self._param_units)}, but got {len(params)}."
            self._numeric_params = BasicVector(params)
        self.DeclareNumericParameter(self._numeric_params)
        # Display parameters
        self.params
    
    @staticmethod
    def _dyn(t,x,u,p,xd):
        FV = p.F/p.V
        k0_exp_C_A2 = p.k0 * np.exp(-p.E/p.R/x.T) * x.C_A**2
        # x_dot
        xd.C_A = FV * (u.C_A0 - x.C_A) - k0_exp_C_A2
        xd.T   = FV * (p.T0 - x.T) - p.dH/p.rho_L/p.C_p * k0_exp_C_A2 + u.Q/p.rho_L/p.C_p/p.V
    
    def DoCalcTimeDerivatives(self, ctx, outp):
        x = self.named_state(ctx.get_continuous_state_vector().get_value())
        u = self.named_inp(self.get_input_port(0).Eval(ctx))
        xd = self.named_state(np.zeros(2))
        p = self.named_params(ctx.get_numeric_parameter(0).get_value())
        self._dyn(None, x, u, p, xd)
        outp.get_mutable_vector().SetFromVector(xd[:])
    
    @staticmethod
    def plot_log(log, inp_log=None, axs=None, figsize=(9,2),
                 labels=[r'$C_A-C_{A_s} (kmol/m^3)$', r'$T-T_s (K)$'],
                 labels_inp=[r'$C_{A0}-C_{A0_s} (kmol/m^3)$', r'$Q-Q_s (kJ/hr)$']):
        if axs is None:
            fig,axs = plt.subplots(1,2 if inp_log is None else 3,figsize=figsize)
        colors = ['C0','C1']
        ts,data = log
        axs[0].plot(ts, data[0],'x-',c=colors[0])
        axs[0].set_xlabel('t (hr)')
        axs[0].set_ylabel(labels[0], color=colors[0])
        axs[0].tick_params(axis='y', labelcolor=colors[0])
        a2 = axs[0].twinx()
        a2.plot(ts, data[1],'x-',c=colors[1])
        a2.set_ylabel(labels[1], color=colors[1])
        a2.tick_params(axis='y', labelcolor=colors[1])
        
        axs[1].plot(data[0], data[1], 'x-', c='k')
        axs[1].plot(data[0][0], data[1][0], 's', c='C2')  # start point
        axs[1].set_xlabel(labels[0])
        axs[1].set_ylabel(labels[1])

        if inp_log is not None:
            ts,data = inp_log
            axs[2].step(ts, data[0],'-',c=colors[0], where='pre')
            axs[2].set_xlabel('t (hr)')
            axs[2].set_ylabel(labels_inp[0], color=colors[0])
            axs[2].tick_params(axis='y', labelcolor=colors[0])
            a2 = axs[2].twinx()
            a2.step(ts, data[1],'--',c=colors[1], where='pre')
            a2.set_ylabel(labels_inp[1], color=colors[1])
            a2.tick_params(axis='y', labelcolor=colors[1])
        try: fig.tight_layout()
        except: pass
