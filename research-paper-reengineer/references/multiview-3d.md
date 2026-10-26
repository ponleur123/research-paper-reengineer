# Specialized checklist: multi-camera, BEV and 3D tracking papers

## Coordinate systems (do not assume)

Enumerate the source paper's frames: camera optical frame, rig/ego frame, local/world frame, BEV cell axes and image pixel coordinates. Write the adopted convention before implementing any projection:

- Column-vector convention: `X_dst_h = T_dst_from_src @ X_src_h`.
- Extrinsic decomposition: `T_dst_from_src = [[R, t], [0, 1]]`.
- Pinhole projection for a camera-frame point: `p ~ K @ [Xc, Yc, Zc]`; `u = p_x/p_z`, `v = p_y/p_z`, for positive depth and a rectified pinhole model.
- General world-to-camera: `X_cam = T_cam_from_world @ X_world`. Camera-to-world is its inverse, not automatically the same matrix.

This is a convention/example, **not proof** that the paper uses it. Check: homogeneous transforms, camera axis directions, left/right-handedness, metric scale, origin, `align_corners`, normalized grid coordinates and resizing/cropping adjustments to K.

## Is calibration required?

Do not infer "BEV implies calibration". Methods using explicit projective mapping typically need camera intrinsics/extrinsics or equivalent transformations, but learned image-to-BEV mapping may use camera parameters, latent geometry, estimated calibration, or no explicit calibrated geometry depending on the formulation. Identify the *actual* operator and trace whether K/T appear in `forward`, in positional embeddings, or only preprocessing. Separate true calibration from rough metadata or learned camera embeddings.

## Multiview aggregation checklist

Capture:

- Backbone features per view: `[B,N,C,H,W]` (illustrative only), feature strides, FPN levels, normalization.
- Matching pixels to 3D/BEV queries: 3D reference points, masks for FOV and depth, attention sampling vs lift-splat, projection order.
- View fusion: sum/mean/max/concat/weighted sum/deformable attention, normalization across valid cameras, what happens when no cameras see a query.
- Positional/time embeddings and camera index embeddings.
- Temporal fusion: frame timestamps, motion compensation, ego-pose transform, memory queue and causal/noncausal windows.
- BEV lattice: origin, bounds, cell size, axes, discretization, center-vs-corner conventions, output dimensions.

Avoid treating feature dimension C as number of views N. A paper's schematic tensor dimensions must be checked against code/configs, not guessed.

## Minimal numeric geometry tests

1. Identity transform produces identical points.
2. `T @ inverse(T) ≈ I` and world→camera→world round trip.
3. A visible 3D point projects to expected pixel for a toy K, `Z>0`.
4. Behind-camera points are masked; zero-depth points never divided blindly.
5. Resize/crop/flip correctly update K or invalidate calibration if appropriate.
6. Different cameras observing the same ground point map to the same chosen world/BEV cell within specified tolerance.
7. Aggregation has explicit handling for all-invalid camera masks.
8. Temporal fusion uses the correct ego-motion direction.

## Tracking extension

If the paper performs tracking, separate detection from association: state representation (x/y/z/yaw/velocity), association cost (IoU/appearance/distance), gating, assignment, track lifecycle, occlusion/re-entry, time delta and identity-switch metrics (e.g. IDF1/HOTA where relevant). Reproducing a detector alone is not reproducing a tracker.
