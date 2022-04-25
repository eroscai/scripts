import coremltools as ct
from coremltools.models.neural_network import quantization_utils

# load full precision model
model_original = ct.models.MLModel('inpaint.mlmodel')

model_fp8 = quantization_utils.quantize_weights(model_original, nbits=8, quantization_mode='linear')
model_fp8.save('inpaint_8_1.mlmodel')