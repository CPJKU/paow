(
~samp_paow = "PATH_TO/audio_euc_markov.wav";

SynthDef("cs", { arg out=0;
    var inA, chainA, inB, chainB, chain, rmod, rewav;
	var  bb;
	bb=Buffer.read(s, ~samp_paow);
	inA = FreeVerb.ar(1 * SoundIn.ar(0) , mix: 0.3, ro om: 1.0, damp: 0.1);
	inA = 1.0 * inA * SinOsc.ar(Saw.kr(0.1, 3, 1));
	inB = 2.5 * PlayBuf.ar(2,bb, rate:1, loop: 0);
	chainA = FFT(LocalBuf(2048), inA);
    chainB = FFT(LocalBuf(2048), inB);
	chain = PV_Max(chainA, PV_MagFreeze(chainB,  SinOsc.kr(Saw.kr(0.1, 3, 1),add:-0.9)));
    rewav = IFFT(chain).dup;
	rmod = 0.15 * rewav;
	Out.ar(out,rmod!2 );
}).play(s);
)