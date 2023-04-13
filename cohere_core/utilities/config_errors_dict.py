# #########################################################################
# Copyright (c) , UChicago Argonne, LLC. All rights reserved.             #
#                                                                         #
# See LICENSE file.                                                       #
# #########################################################################

"""
Error dictionaries and lookup map name dictionary
"""
__author__ = "David Cyl"
__copyright__ = "Copyright (c) 2016, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'

config_error = {'File':['File does not exist','Cannot Read File',
                        'Parsing error, check parenthesis,quotation syntax'],
                'Workingdir':['working_dir parameter should be a string',
                              'missing mandatory working_dir parameter'],
                'ExperimentID':['experiment_id parameter should be string',
                                'missing mandatory experiment_id parameter'],
                'Scan':['scan parameter should be a string',
                        'scan parameter parsing error'],
                'Specfile':['specfile parameter should be string',
                            'specfile parameter parsing error']}
config_prep_error = {'File':['No configuration file',
                             'cannot read configuration file',
                             'Parsing error, check parenthesis,quotation syntax'],
                     'Roi':['roi parameter should be a list of int'],
                     'Datadir':['data_dir parameter should be string',
                                'missing mandatory parameter data_dir'],
                     'Darkfield':['darkfield_filename parameter should be string',
                                  'darkfield_filename parameter parsing error'],
                     'Whitefield':['whitefield_filename parameter should be string',
                                   'whitefield_filename parameter parsing error'],
                     'Excludescans':['exclude scans should be a list'],
                     'MinFiles':['min_files should be int',
                                 'min_files parameter parsing error'],
                     'Separatescans':['separate_scans parameter should be True or False'],
                     'Separatescanranges':['separate_scan_ranges parameter should be True or False']}
config_disp_error = {'File':['No configuration file',
                             'Cannot read configuration file',
                             'Parsing error, check parenthesis,quotation syntax'],
                     'Resultsdir':['results_dir parameter should be string'],
                     'Diffractometer':['diffractometer parameter should be string'],
                     'Detector':['detector parameter should be string'],
                     'Crop':['crop should be list',
                             'crop should be a list of int or float'],
                     'Rampups':['rampups should be int'],
                     'Energy':['energy should be float',
                               'energy parameter parsing error'],
                     'Delta':['delta should be float',
                              'delta parameter parsing error'],
                     'Gamma':['gamma should be float',
                              'gamma parameter parsing error'],
                     'Detdist':['detdist should be float',
                                'detdist parameter parsing error'],
                     'Dth':['dth should be float',
                            'dth parameter parsing error']}
config_data_error = {'File':['No configuration file',
                             'Cannot read configuration file',
                             'Parsing error, check parenthesis,quotation syntax'],
                     'Datadir':['data_dir parameter should be string',
                                'data_dir parameter parsing error'],
                     'Adjustdimensions':['adjust_dimensions should be a list of int'],
                     'Centershift':['center_shift should be a list of int'],
                     'Binning':['binning should be a list of int'],
                     'Intensitythreshold':['intensity_threshold should be float or int',
                                           'missing mandatory parameter intensity_threshold'],
                     'Alienalg':['alien_alg can only be one the following strings: "block_aliens", "alien_file", "AutoAlien1", "none"'],
                     'Aliens':['aliens should be a list of alien blocks (lists)',
                               'aliens is not a list of ints',
                               'misconfigured alien, each alien is defined by list of six int for 3D data',
                               '"aliens" parameter must be configured if "block_aliens" selected'],
                     'AlienFile':['alien_file should be a string (mask file name)',
                                  '"alien_file" parameter must be configured if "alien_file" selected'],
                     'Aa1sizethreshold':['AA1_size_threshold should be float',
                                         'AA1_size_threshold parameter parsing error'],
                     'Aa1asymthreshold':['AA1_asym_threshold should be float',
                                         'AA1_asym_threshold parameter parsing error'],
                     'Aa1minpts':['AA1_min_pts should be int',
                                  'AA1_min_pts parameter parsing error'],
                     'Aa1eps':['AA1_eps should be float',
                               'AA1_eps parameter parsing error'],
                     'Aa1ampthreshold':['AA1_amp_threshold should be float',
                                        'AA1_amp_threshold parameter parsing error'],
                     'Aa1savearrs':['AA1_save_arrs parameter should be True or False',
                                    'AA1_save_arrs parameter parsing error'],
                     'Aa1expandcleanedsigma':['AA1_expandcleanedsigma should be float',
                                              'AA1_expandcleanedsigma parameter parsing error']}
config_rec_error = {'File':['No configuration file',
                             'Cannot read configuration file',
                             'Parsing error, check parenthesis,quotation syntax'],
                    'Datadir':['data_dir parameter should be string',
                               'configured data_dir is not a directory',
                               'no data file found in data_dir'],
                    'Savedir':['save_dir parameter should be string',
                               'save_dir parameter parsing error'],
                    'Initguess':['init_guess parameter should be one of the following strings: "random", "continue", "AI_guess"'],
                    'Continuedir':['continue_dir parameter should be string',
                                   'continue_dir parameter is mandatory when init_guess is "continue"'],
                    'Aitrainedmodel':['AI_trained_model parameter should be string',
                                   'AI_trained_model parameter is mandatory when init_guess is "AI algorithm"'],
                    'Reconstruction':['reconstructions parameter should be int',
                                      'reconstructions parameter parsing error'],
                    'Device':['device not a list of ints',
                              'device parameter parsing error'],
                    'Algorithmsequence':['algorithm_sequence should be string',
                                         'algorithm_sequence configuration error, only numerical, digital, and the following characters: *, +, (, ), space, are allowed ',
                                         'algorithm_sequence configuration error, check brackets, nested brackets not supported',
                                         'missing mandatory algorithm_sequence parameter'],
                    'Hiobeta':['hio_beta parameter should be float'],
                    'Initialsupportarea':['initial_support_area should be list',
                                          'initial_support_area should be a list of int or float'],
                    'Generations':['ga_generations parameter should be int',
                                   'when running GA "reconstructions" parameter should be configured and greater than 1'],
                    'Gametrics':['ga_metrics is not a list',
                                 'warning: ga_metrics list can include only following strings: "chi", "sharpness", "summed_phase", "area"'],
                    'Gabreedmodes':['ga_breed_mode is not a list',
                                    'warning: ga_breed_modes list can include only following strings: “none”, “sqrt_ab”, “pixel_switch”, “b_pa”, “2ab_a_b”, “2a_b_pa”,'
                                    ' “sqrt_ab_pa”, “sqrt_ab_pa_recip”, “sqrt_ab_recip”,“max_ab”, “max_ab_pa”, '
                                    '“min_ab_pa”, “avg_ab”, “avg_ab_pa"'],
                    'Gacullings':['ga_cullings parameter should be a ist of int',
                                  'sum of all cullings should be smaller than number of reconstructions'],
                    'Gashrinkwrapthresholds':['ga_sw_thresholds parameter should be a list of floats'],
                    'Gashrinkwrapgausssigmas':['ga_sw_gauss_sigmas parameter should be a list of floats'],
                    'Galowpassfiltersigmas':['List Float Error',
                                             'ga_sw_gauss_sigmas parameter parsing error'],
                    'Gagenpcstart':['ga_gen_pc_start parameter should be int',
                                    'ga_gen_pc_start parameter parsing error'],
                    'Twintrigger':['Trigger should be a list of int'],
                    'Twinhalves':['twin_halves should be a list of int'],
                    'Shrinkwraptrigger':['Trigger should be a list of int',
                                         'Each sub-trigger should be a list of int if multiple shrink wraps'],
                    'Shrinkwraptype':['sw_type parameter should be string',
                                      'supporting sw_type "GAUSS"'],
                    'Shrinkwrapthreshold':['sw_threshold should be float',
                                           'sw_threshold should be a list of floats if multiple shrink wraps'],
                    'Shrinkwrapgausssigma':['sw_gauss_sigma should be float',
                                            'sw_gauss_sigma should be a list of floats if multiple shrink wraps'],
                    'Phasesupporttrigger':['Trigger should be a list of int',
                                           'Each sub-trigger should be a list of int if multiple phase modulus'],
                    'Phmphasemin':['phm_phase_min should be float',
                                   'phm_phase_min should be a list of floats if multiple phase modulus'],
                    'Phmphasemax':['phm_phase_max should be float',
                                   'phm_phase_max should be a list of floats if multiple phase modulus'],
                    'Pcinterval':['pc_interval should be int'],
                    'Pctype':['pc_type parameter should be string',
                              'pc_type parameter can be configured "LUCY"',
                              'pc_type parameter parsing error'],
                    'Pclucyiterations':['pc_LUCY_iterations should be int',
                                       'pc_LUCY_iterations parameter parsing error'],
                    'Pcnormalize':['pc_normalize parameter should be True or False',
                                   'pc_normalize parameter parsing error'],
                    'Pclucykernel':['pc_LUCY_kernel parameter should be a list of int',
                                    'pc_LUCY_kernel parameter must be configured when partial coherence feature in active'],
                    'lpftrigger':['Trigger should be a list of int',
                                    'Each sub-trigger should be a list of int if multiple lowpass filters'],
                    'Lowpassfilterswthreshold':['lpf_sw_threshold parameter should be flot',
                                                'lpf_sw_threshold should be a list of floats if multiple lowpass filters'],
                    'Lowpassfilterrange':['lowpass_filter_range parameter should be list of flots',
                                          'lowpass_filter_range should be a list of int for each lowpass filter if multiple lowpass filters'
                                          'missing lowpass_filter_range parameter'],
                    'Averagetrigger':['Trigger should be a list of int'],
                    'Progresstrigger':['Trigger should be a list of int'],
                    }

config_map_names = {'config_error_map_file':config_error,
                    'config_prep_error_map_file':config_prep_error,
                    'config_disp_error_map_file':config_disp_error,
                    'config_data_error_map_file':config_data_error,
                    'config_rec_error_map_file':config_rec_error}
