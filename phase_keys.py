#import coinstac_node_ops.local as ops_local
#import coinstac_node_ops.remote as ops_remote

import coinstac_spatially_constrained_ica.local as scica_local
import coinstac_spatially_constrained_ica.remote as scica_remote

# Init

# Spatially Constrained ICA
SPATIALLY_CONSTRAINED_ICA_LOCAL = [
    dict(
        do=[
            scica_local.scica_local_phases,
            #ops_local.local_output_to_cache,
            #ops_local.local_dump_cache_to_npy,
            #ops_local.local_clear_cache
        ],
        recv=[],
        send='scica_local_XXXX',
        args=[
            [],
            [],
            [],
            []
        ],
        kwargs=[
            {},
            {},
            {},
            {}
        ],
    )
]
SPATIALLY_CONSTRAINED_ICA_REMOTE = [
    dict(
        do=[
            scica_remote.scica_remote_phases,
        ],
        recv=SPATIALLY_CONSTRAINED_ICA_LOCAL[0].get('send'),
        send='scica_remote_XXXX',
        args=[
            []
        ],
        kwargs=[
            {}
        ],
    )
]

