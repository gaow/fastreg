import numpy as np
from scipy import stats

import utils


def fit(xdata, ydata):
    """Calculate 2D regression.

    Args:
        xdata (numpy.ndarray): 1D array of independent data [ntim],
            where ntim is the number of time points (or other independent
            points).
        ydata (numpy.ndarray): 2D array of dependent data [ntim, nspat],
            where nspat is the number of spatial points (or other dependent
            points).
     
    Returns:
        numpy.ndarray of dimension [5, nspat].  The 5 outputs are: slope, 
        intercept, Pearson's correlation coefficient, two-sided p-value for
        a hypothesis test with null hypothesis that the slope is zero, 
        standard error for the slope estimate.

    """
    # Small number to prevent divide-by-zero errors
    TINY = 1.0e-20

    # Dimensions
    ntim = xdata.shape[0]
    nspat = ydata.shape[1]

    # Add a constant (1) to the xdata to allow for intercept calculation
    xdata_plus_const = utils.add_constant(xdata)

    # Calculate parameters of the regression by solving the OLS problem
    # in its matrix form
    mat1 = np.swapaxes(np.dot(xdata_plus_const.T,
                              (xdata_plus_const[np.newaxis, :, :])), 0, 1)
    mat2 = np.dot(xdata_plus_const.T, ydata)
    beta = np.linalg.solve(mat1, mat2.T)
    output = beta.T

    # Pearson correlation coefficient
    xm, ym = xdata-xdata.mean(0), ydata-ydata.mean(0)
    r_num = np.dot(xm, ym)
    r_den = np.sqrt(stats.ss(xm) * stats.ss(ym))
    pearson_r = r_num / r_den

    # Two-sided p-value for a hypothesis test whose null hypothesis is that
    # the slope is zero.
    df = ntim - 2
    tval = pearson_r * np.sqrt(df / ((1.0 - pearson_r + TINY) *
                                     (1.0 + pearson_r + TINY)))
    pval = stats.distributions.t.sf(np.abs(tval), df)*2

    # Standard error of the slope estimate
    sst = np.sum(ym ** 2, 0)
    ssr = (output[0, :] ** 2) * np.sum(xm ** 2)
    se = np.sqrt((1. / df) * (sst - ssr))
    stderr = se / np.sqrt(np.sum(xm ** 2))

    return np.vstack([output, pearson_r, pval, stderr])
