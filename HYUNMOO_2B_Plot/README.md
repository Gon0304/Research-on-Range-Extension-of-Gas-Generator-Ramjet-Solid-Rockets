Testing with Fuel: HYDROGEN
============================================================

============================================================
Selected Model : Hyunmoo-2B-class SRBM
Propulsion     : two-stage solid
Fuel Type      : hydrogen
Length         : 12.000 m
Diameter       : 0.900 m
Launch mass    : 5400.0 kg
Dry mass       : 2268.0 kg
Prop mass      : 3132.0 kg
Solid ratio    : 0.70
Gas ratio      : 0.30
Area           : 0.6362 m^2
Solid thrust   : 119445.0 N
Ramjet T_ref   : 36789.1 N
Ramjet LHV     : 120.00 MJ/kg
Ramjet Isp     : 4229.5 s
============================================================


 *********** MPOPT Summary ********** 

CasADi - 2026-05-10 17:13:05 WARNING("The options 't0', 'tf', 'grid' and 'output_t0' have been deprecated.
The same functionality is provided by providing additional input arguments to the 'integrator' function, in particular:
 * Call integrator(..., t0, tf, options) for a single output time, or
 * Call integrator(..., t0, grid, options) for multiple grid points.
The legacy 'output_t0' option can be emulated by including or excluding 't0' in 'grid'.
Backwards compatibility is provided in this release only.") [.../casadi/core/integrator.cpp:698]
CasADi - 2026-05-10 17:13:05 WARNING("solver:nlp_jac_g failed: NaN detected for output jac_g_x, at nonzero index 668 (row 182, col 121).") [.../casadi/core/oracle_function.cpp:408]
CasADi - 2026-05-10 17:13:05 WARNING("solver:nlp_jac_g failed: NaN detected for output jac_g_x, at nonzero index 668 (row 182, col 121).") [.../casadi/core/oracle_function.cpp:408]
 Optimal cost (J):  -96658.3 

 Solved in 1489.373 ms
         OCP transcription time  : 358.592 ms
         NLP solution time       : 1130.781 ms

 Post processed in 142.553 ms
         Solution retrieval            : 0.224 ms
         Process solution and plot      : 142.328 ms

==================== Result Summary ====================
Model              : Hyunmoo-2B-class SRBM
Fuel Type          : hydrogen
Gas ratio          : 0.30
Final range        : 96.690 km
Final altitude     : 0.000 m
Terminal velocity  : 449.976 m/s
Terminal gamma     : -10.000 deg
Final mass         : 3143.061 kg
Final time         : 120.000 s
========================================================


========== Trajectory Summary ==========
Final time              : 120.000 s
Final range             : 96.690 km
Max altitude            : 8.017 km
Terminal altitude       : 0.000 m
Initial velocity        : 552.986 m/s
Max velocity            : 1143.694 m/s
Terminal velocity       : 449.976 m/s
Initial mass            : 5400.000 kg
Final mass              : 3143.061 kg
Min gamma               : -10.000 deg
Max gamma               : 30.000 deg
Min alpha               : -2.000 deg
Max alpha               : 2.000 deg
Min throttle            : 0.240
Max throttle            : 1.000
========================================


============================================================
Testing with Fuel: METHANE
============================================================

============================================================
Selected Model : Hyunmoo-2B-class SRBM
Propulsion     : two-stage solid
Fuel Type      : methane
Length         : 12.000 m
Diameter       : 0.900 m
Launch mass    : 5400.0 kg
Dry mass       : 2268.0 kg
Prop mass      : 3132.0 kg
Solid ratio    : 0.70
Gas ratio      : 0.30
Area           : 0.6362 m^2
Solid thrust   : 119445.0 N
Ramjet T_ref   : 36789.1 N
Ramjet LHV     : 50.00 MJ/kg
Ramjet Isp     : 2730.1 s
============================================================


 *********** MPOPT Summary ********** 

CasADi - 2026-05-10 17:13:14 WARNING("solver:nlp_jac_g failed: NaN detected for output jac_g_x, at nonzero index 668 (row 182, col 121).") [.../casadi/core/oracle_function.cpp:408]
CasADi - 2026-05-10 17:13:14 WARNING("solver:nlp_jac_g failed: NaN detected for output jac_g_x, at nonzero index 668 (row 182, col 121).") [.../casadi/core/oracle_function.cpp:408]
 Optimal cost (J):  -93607.6 

 Solved in 1367.533 ms
         OCP transcription time  : 163.88 ms
         NLP solution time       : 1203.653 ms

 Post processed in 34.387 ms
         Solution retrieval            : 0.227 ms
         Process solution and plot      : 34.159 ms

==================== Result Summary ====================
Model              : Hyunmoo-2B-class SRBM
Fuel Type          : methane
Gas ratio          : 0.30
Final range        : 93.637 km
Final altitude     : 0.000 m
Terminal velocity  : 416.962 m/s
Terminal gamma     : -10.000 deg
Final mass         : 3135.267 kg
Final time         : 120.000 s
========================================================


========== Trajectory Summary ==========
Final time              : 120.000 s
Final range             : 93.637 km
Max altitude            : 7.710 km
Terminal altitude       : 0.000 m
Initial velocity        : 552.986 m/s
Max velocity            : 1137.975 m/s
Terminal velocity       : 416.962 m/s
Initial mass            : 5400.000 kg
Final mass              : 3135.267 kg
Min gamma               : -10.000 deg
Max gamma               : 30.000 deg
Min alpha               : -2.000 deg
Max alpha               : 2.000 deg
Min throttle            : 0.240
Max throttle            : 1.000
========================================


============================================================
Testing with Fuel: ETHYLENE
============================================================

============================================================
Selected Model : Hyunmoo-2B-class SRBM
Propulsion     : two-stage solid
Fuel Type      : ethylene
Length         : 12.000 m
Diameter       : 0.900 m
Launch mass    : 5400.0 kg
Dry mass       : 2268.0 kg
Prop mass      : 3132.0 kg
Solid ratio    : 0.70
Gas ratio      : 0.30
Area           : 0.6362 m^2
Solid thrust   : 119445.0 N
Ramjet T_ref   : 36789.1 N
Ramjet LHV     : 47.00 MJ/kg
Ramjet Isp     : 2646.9 s
============================================================


 *********** MPOPT Summary ********** 

CasADi - 2026-05-10 17:13:20 WARNING("solver:nlp_jac_g failed: NaN detected for output jac_g_x, at nonzero index 668 (row 182, col 121).") [.../casadi/core/oracle_function.cpp:408]
CasADi - 2026-05-10 17:13:20 WARNING("solver:nlp_jac_g failed: NaN detected for output jac_g_x, at nonzero index 668 (row 182, col 121).") [.../casadi/core/oracle_function.cpp:408]
 Optimal cost (J):  -93191.5 

 Solved in 1370.463 ms
         OCP transcription time  : 161.544 ms
         NLP solution time       : 1208.919 ms

 Post processed in 34.303 ms
         Solution retrieval            : 0.224 ms
         Process solution and plot      : 34.074 ms

==================== Result Summary ====================
Model              : Hyunmoo-2B-class SRBM
Fuel Type          : ethylene
Gas ratio          : 0.30
Final range        : 93.220 km
Final altitude     : 0.000 m
Terminal velocity  : 412.489 m/s
Terminal gamma     : -10.000 deg
Final mass         : 3136.060 kg
Final time         : 120.000 s
========================================================


========== Trajectory Summary ==========
Final time              : 120.000 s
Final range             : 93.220 km
Max altitude            : 7.731 km
Terminal altitude       : 0.000 m
Initial velocity        : 552.986 m/s
Max velocity            : 1138.140 m/s
Terminal velocity       : 412.489 m/s
Initial mass            : 5400.000 kg
Final mass              : 3136.060 kg
Min gamma               : -10.000 deg
Max gamma               : 30.000 deg
Min alpha               : -2.000 deg
Max alpha               : 2.000 deg
Min throttle            : 0.240
Max throttle            : 1.000
========================================


============================================================
Testing with Fuel: KEROSENE
============================================================

============================================================
Selected Model : Hyunmoo-2B-class SRBM
Propulsion     : two-stage solid
Fuel Type      : kerosene
Length         : 12.000 m
Diameter       : 0.900 m
Launch mass    : 5400.0 kg
Dry mass       : 2268.0 kg
Prop mass      : 3132.0 kg
Solid ratio    : 0.70
Gas ratio      : 0.30
Area           : 0.6362 m^2
Solid thrust   : 119445.0 N
Ramjet T_ref   : 36789.1 N
Ramjet LHV     : 43.00 MJ/kg
Ramjet Isp     : 2531.8 s
============================================================


 *********** MPOPT Summary ********** 

CasADi - 2026-05-10 17:13:26 WARNING("solver:nlp_jac_g failed: NaN detected for output jac_g_x, at nonzero index 668 (row 182, col 121).") [.../casadi/core/oracle_function.cpp:408]
CasADi - 2026-05-10 17:13:26 WARNING("solver:nlp_jac_g failed: NaN detected for output jac_g_x, at nonzero index 668 (row 182, col 121).") [.../casadi/core/oracle_function.cpp:408]
 Optimal cost (J):  -92710.9 

 Solved in 1353.384 ms
         OCP transcription time  : 162.556 ms
         NLP solution time       : 1190.828 ms

 Post processed in 37.61 ms
         Solution retrieval            : 0.227 ms
         Process solution and plot      : 37.382 ms

==================== Result Summary ====================
Model              : Hyunmoo-2B-class SRBM
Fuel Type          : kerosene
Gas ratio          : 0.30
Final range        : 92.740 km
Final altitude     : 0.000 m
Terminal velocity  : 407.149 m/s
Terminal gamma     : -10.000 deg
Final mass         : 3137.042 kg
Final time         : 120.000 s
========================================================


========== Trajectory Summary ==========
Final time              : 120.000 s
Final range             : 92.740 km
Max altitude            : 7.809 km
Terminal altitude       : 0.000 m
Initial velocity        : 552.986 m/s
Max velocity            : 1139.073 m/s
Terminal velocity       : 407.149 m/s
Initial mass            : 5400.000 kg
Final mass              : 3137.042 kg
Min gamma               : -10.000 deg
Max gamma               : 30.000 deg
Min alpha               : -2.000 deg
Max alpha               : 2.000 deg
Min throttle            : 0.240
Max throttle            : 1.000
========================================
