from model import PopMusicTransformer
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
import random 

def main():
    # declare model
    model = PopMusicTransformer(
        checkpoint='checkpoint',
        is_training=False)
    
    # generate from scratch
    for i in range(500):
        #randomly choose a tempreture between 1 and 2
        temp = random.uniform(1, 2)
        model.generate(
            n_target_bar=16,
            temperature=temp,
            topk=5,
            output_path='./2nd_round/gen_from_26_3_0_temp{}_{}.midi'.format(temp, i),
            prompt=None)
    
    # close model
    model.close()

if __name__ == '__main__':
    main()