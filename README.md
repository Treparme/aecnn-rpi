
# BUILD ON: 
# Real-time Python framework for speech enhancement using AECNNs

Fotios Drakopoulos, Deepak Baby and Sarah Verhulst. Real-time audio processing on a Raspberry Pi using deep neural
networks, 23rd International Congress on Acoustics, 9 to 13 September 2019 in Aachen, Germany.

This work received funding from the European Research Council (ERC) under the Horizon 2020 Research and Innovation Programme (grant agreement No 678120 RobSpear)

----

The Keras framework for the implementation of the AECNN models is adapted from [here](https://github.com/deepakbaby/se_relativisticgan). The necessary scripts can be found in the AECNN folder.

# start_jackd.sh
Deze dient op de jack client klaar te zetten, zet parameters goed voor de audiokaart

# audio_processing.py

run via: "python3 audio_processing.py -n 1024 (of grotere macht van 2)

-n is windowsize

de belangrijkste,

hebben 2 inputs, 2 outputs, deze werken via queues

wanneer deze crasht (ergens foutloopt) en we herstarten kan het zijn dat de server/socket niet gevonden wordt, het best is dan nog eens opnieuw proberen te runnen

lijnen 157-158 zijn het belangrijkste voor het algoritme tussen te plaatsen!!
2 queues om input van te halen, 2 queues om output naar buiten mee te brengen
