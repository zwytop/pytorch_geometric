import torch
from torch_geometric.nn import knn
from torch_scatter import scatter_add


def knn_interpolate(x, pos_x, pos_y, batch_x=None, batch_y=None, k=3):
    r"""The k-NN interpolation from the `"PointNet++: Deep Hierarchical
    Feature Learning on Point Sets in a Metric Space"
    <https://arxiv.org/abs/1706.02413>`_ paper.
    For each point :obj:`y`, its interpolated features are given by

    .. math::
        f(\mathbf{x}) = \frac{\sum_{i=1}^k w_i(y) f_i}{\sum_{i=1}^k w_i(y)}
        \textrm{, where } w_i(y) = \frac{1}{d(y, x_i)^2}.

    Args:
        x (Tensor): Node feature matrix
            :math:`\mathbf{X} \in \mathbb{R}^{N \times F}`.
        pos_x (Tensor): Node position matrix
            :math:`\in \mathbb{R}^{N \times d}`.
        pos_y (Tensor): Upsampled node position matrix
            :math:`\in \mathbb{R}^{M \times d}`.
        batch_x (LongTensor, optional): Batch vector
            :math:`\mathbf{b_x} \in {\{ 0, \ldots, B-1\}}^N`, which assigns
            each node from :math:`\mathbf{X}` to a specific example.
            (default: :obj:`None`)
        batch_y (LongTensor, optional): Batch vector
            :math:`\mathbf{b_y} \in {\{ 0, \ldots, B-1\}}^N`, which assigns
            each node from :math:`\mathbf{Y}` to a specific example.
            (default: :obj:`None`)
        k (int, optional): Number of neighbors. (default: :obj:`3`)

    :rtype: :class:`Tensor`
    """

    with torch.no_grad():
        y_idx, x_idx = knn(pos_x, pos_y, k, batch_x=batch_x, batch_y=batch_y)
        diff = pos_x[x_idx] - pos_y[y_idx]
        squared_distance = (diff * diff).sum(dim=-1, keepdim=True)
        print(squared_distance)
        weights = 1.0 / torch.clamp(squared_distance, min=1e-16)

    # print(weights)
    print(x)
    y = scatter_add(x[x_idx] * weights, y_idx, dim=0, dim_size=pos_y.size(0))
    y = y / scatter_add(weights, y_idx, dim=0, dim_size=pos_y.size(0))

    return y
