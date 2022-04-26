import coremltools as ct
from coremltools.models.neural_network import quantization_utils
import argparse

def main(cfg):
    input_path = cfg.input_path
    output_path = cfg.output_path

    # load full precision model
    model_original = ct.models.MLModel(input_path)

    model_fp8 = quantization_utils.quantize_weights(model_original, nbits=16, quantization_mode='linear')
    model_fp8.save(output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, default=None)
    parser.add_argument('--output_path', type=str, default=None)
    config = parser.parse_args()
    main(config)