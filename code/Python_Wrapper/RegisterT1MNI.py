import broccoli
import numpy
import scipy
from nibabel import nifti1

from operator import mul

def registerT1MNI(
    h_T1_Data,          # Array
    h_MNI_Data,         # Array
    h_MNI_Brain,        # double
    h_MNI_Brain_Mask,   # double
    h_Quadrature_Filter_Parametric_Registration,            # 3 elements, complex arrays
    h_Quadrature_Filter_NonParametric_Registration,         # 6 elements, complex arrays
    h_Projection_Tensor,             # 6 elements
    h_Filter_Directions,             # 3 elements
    NUMBER_OF_ITERATIONS_FOR_PARAMETRIC_IMAGE_REGISTRATION,     # int
    NUMBER_OF_ITERATIONS_FOR_NONPARAMETRIC_IMAGE_REGISTRATION,  # int
    COARSEST_SCALE,         # int
    MM_T1_Z_CUT,            # int
    OPENCL_PLATFORM,        # int
    OPENCL_DEVICE,          # int
  ):
  
  BROCCOLI = broccoli.BROCCOLI_LIB()
  BROCCOLI.GetOpenCLInfo()
  print(BROCCOLI.GetOpenCLDeviceInfoChar())
  print("Initializing OpenCL...")
  
  BROCCOLI.OpenCLInitiate(OPENCL_PLATFORM, OPENCL_DEVICE)
  ok = BROCCOLI.GetOpenCLInitiated()
  
  if ok == 0:
    BROCCOLI.printSetupErrors()
    print("OpenCL initialization failed, aborting")
    return

  print("OpenCL initialization successful, proceeding...")
  
  ## Set constants
  NUMBER_OF_AFFINE_IMAGE_REGISTRATION_PARAMETERS = 12
  MNI_DATA_SIZE = reduce(mul, h_MNI_Data.dimensions, 1)
  
  ## Pass input parameters to BROCCOLI
  print("Setting up input parameters...")
  
  BROCCOLI.SetT1Data(h_T1_Data)
  BROCCOLI.SetMNIData(h_MNI_Data)
  BROCCOLI.SetInputMNIBrainVolume(h_MNI_Brain.toFloatArray())
  BROCCOLI.SetInputMNIBrainMask(h_MNI_Brain_Mask.toFloatArray())
  
  BROCCOLI.SetInterpolationMode(broccoli.LINEAR) # Linear
  BROCCOLI.SetNumberOfIterationsForParametricImageRegistration(NUMBER_OF_ITERATIONS_FOR_PARAMETRIC_IMAGE_REGISTRATION)
  BROCCOLI.SetNumberOfIterationsForNonParametricImageRegistration(NUMBER_OF_ITERATIONS_FOR_NONPARAMETRIC_IMAGE_REGISTRATION)
  
  BROCCOLI.SetImageRegistrationFilterSize(h_Quadrature_Filter_Parametric_Registration[0][0].dimensions[0])
  BROCCOLI.SetParametricImageRegistrationFilters(h_Quadrature_Filter_Parametric_Registration)
  BROCCOLI.SetNonParametricImageRegistrationFilters(h_Quadrature_Filter_NonParametric_Registration)
  
  BROCCOLI.SetProjectionTensorMatrixFilters(h_Projection_Tensor)
  BROCCOLI.SetFilterDirections(*h_Filter_Directions)
  
  BROCCOLI.SetCoarsestScaleT1MNI(COARSEST_SCALE)
  BROCCOLI.SetMMT1ZCUT(MM_T1_Z_CUT)
    
  ## Set up output parameters
  print("Setting up output parameters...")
  
  h_Aligned_T1_Volume = broccoli.floatArray(MNI_DATA_SIZE)
  BROCCOLI.SetOutputAlignedT1Volume(h_Aligned_T1_Volume)
  
  h_Aligned_T1_Volume_NonParametric = broccoli.floatArray(MNI_DATA_SIZE)
  BROCCOLI.SetOutputAlignedT1VolumeNonParametric(h_Aligned_T1_Volume_NonParametric)
  
  h_Skullstripped_T1_Volume = broccoli.floatArray(MNI_DATA_SIZE)
  BROCCOLI.SetOutputSkullstrippedT1Volume(h_Skullstripped_T1_Volume)
  
  h_Interpolated_T1_Volume = broccoli.floatArray(MNI_DATA_SIZE)
  BROCCOLI.SetOutputInterpolatedT1Volume(h_Interpolated_T1_Volume)

  # Not used in broccoli_lib.cpp  
  # h_Downsampled_Volume = broccoli.floatArray(MNI_DATA_SIZE)
  # BROCCOLI.SetOutputDownsampledVolume(h_Downsampled_Volume)
  
  h_Registration_Parameters = broccoli.floatArray(12)
  BROCCOLI.SetOutputT1MNIRegistrationParameters(h_Registration_Parameters)
  
  # Not used in broccoli_lib.cpp
  # h_Quadrature_Filter_Response = [broccoli.cl_float2Array(10) for i in range(6)]
  # BROCCOLI.SetOutputQuadratureFilterResponses(*h_Quadrature_Filter_Response)
  
  # h_OutputTensor = [broccoli.floatArray(10) for i in range(6)]
  # BROCCOLI.SetOutputTensorComponents(*h_OutputTensor)
  
  # h_Displacement_Field = [broccoli.floatArray(10) for i in range(3)]
  # BROCCOLI.SetOutputDisplacementField(*h_Displacement_Field)
  
  h_Phase_Differences = broccoli.floatArray(10)
  BROCCOLI.SetOutputPhaseDifferences(h_Phase_Differences)
  
  h_Phase_Certainties = broccoli.floatArray(10)
  BROCCOLI.SetOutputPhaseCertainties(h_Phase_Certainties)
  
  h_Phase_Gradients = broccoli.floatArray(10)
  BROCCOLI.SetOutputPhaseGradients(h_Phase_Gradients)
  
  h_Slice_Sums = broccoli.floatArray(10)
  BROCCOLI.SetOutputSliceSums(h_Slice_Sums)
  
  h_Top_Slice = broccoli.floatArray(10)
  BROCCOLI.SetOutputTopSlice(h_Top_Slice)
  
  h_A_Matrix = broccoli.floatArray(NUMBER_OF_AFFINE_IMAGE_REGISTRATION_PARAMETERS * NUMBER_OF_AFFINE_IMAGE_REGISTRATION_PARAMETERS)
  BROCCOLI.SetOutputAMatrix(h_A_Matrix)
  
  h_h_Vector = broccoli.floatArray(NUMBER_OF_AFFINE_IMAGE_REGISTRATION_PARAMETERS)
  BROCCOLI.SetOutputHVector(h_h_Vector)

  ## Perform registration
  print("Performing registration...")
  BROCCOLI.PerformRegistrationT1MNINoSkullstripWrapper()
  
  print("\n##  Registration performed!  ##\n")
  BROCCOLI.printRunErrors()
  
  return (h_Aligned_T1_Volume, h_Aligned_T1_Volume_NonParametric, h_Skullstripped_T1_Volume, h_Interpolated_T1_Volume, 
          h_Registration_Parameters, h_Phase_Differences, h_Phase_Certainties, h_Phase_Gradients, h_Slice_Sums, h_Top_Slice, h_A_Matrix, h_h_Vector)
  
if __name__ == "__main__":
  opencl_platform = 0
  opencl_device = 0
  
  study = 'Cambridge'
  subject = 'sub00156'
  voxel_size = 2
  MNI_voxel_sizes = [voxel_size] * 3
  
  number_of_iterations_for_parametric_image_registration = 10
  number_of_iterations_for_nonparametric_image_registration = 15
  coarsest_scale = 8 / voxel_size
  MM_T1_Z_CUT = 30
  
  MNI_nni = nifti1.load('../../brain_templates/MNI152_T1_%dmm.nii' % voxel_size)
  MNI = broccoli.arrayFromNifti(MNI_nni, MNI_voxel_sizes)
  
  MNI_brain_nii = nifti1.load('../../brain_templates/MNI152_T1_%dmm_brain.nii' % voxel_size)
  MNI_brain = broccoli.arrayFromNifti(MNI_brain_nii, MNI_voxel_sizes)
  
  MNI_brain_mask_nii = nifti1.load('../../brain_templates/MNI152_T1_%dmm_brain_mask.nii' % voxel_size)
  MNI_brain_mask = broccoli.arrayFromNifti(MNI_brain_mask_nii, MNI_voxel_sizes)
  
  T1_nni = nifti1.load('../../test_data/fcon1000/classic/%s/%s/anat/mprage_skullstripped.nii.gz' % (study, subject))
  T1 = broccoli.arrayFromNifti(T1_nni, MNI_voxel_sizes)
  
  filters_parametric_mat = scipy.io.loadmat("../Matlab_Wrapper/filters_for_parametric_registration.mat")
  filters_nonparametric_mat = scipy.io.loadmat("../Matlab_Wrapper/filters_for_nonparametric_registration.mat")
  
  parametric_filters = [[broccoli.Array(d) for d in filters_parametric_mat['f%d_parametric_registration' % (i+1)]] for i in range(3)]
  nonparametric_filters = [[broccoli.Array(d) for d in filters_nonparametric_mat['f%d_nonparametric_registration' % (i+1)]] for i in range(6)]
  
  results = registerT1MNI(T1, MNI, MNI_brain, MNI_brain_mask, parametric_filters, nonparametric_filters,
                [filters_nonparametric_mat['m%d' % (i+1)][0] for i in range(6)], 
                [broccoli.floatArrayFromList(filters_nonparametric_mat['filter_directions_%s' % d][0]) for d in ['x', 'y', 'z']],
                number_of_iterations_for_parametric_image_registration,
                number_of_iterations_for_nonparametric_image_registration,
                coarsest_scale,
                MM_T1_Z_CUT,
                opencl_platform,
                opencl_device)

  for r in results:
    print(r)