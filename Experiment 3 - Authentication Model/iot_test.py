import pandas as pd
import numpy as np
from autogluon.tabular import TabularPredictor

classification = TabularPredictor.load("../models/classification")
impersonation_detection = TabularPredictor.load("../models/impersonation_detection")
authenticator = TabularPredictor.load("../models/authenticator")

classification.persist()
impersonation_detection.persist()
authenticator.persist()

np.random.seed(29)

def main():


    genuine_testing_df = pd.read_csv('genuine_testing.csv')
    impersonator_testing_df = pd.read_csv('impersonator_testing.csv')

    print(genuine_testing_df['label'].unique())

    

    for node in list(genuine_testing_df['label'].unique()):
        test_authenticator_models(genuine_testing_df, node, 'genuine')


def test_authenticator_models(testing_df: pd.DataFrame, node_id: str, test_type: str) -> None:
    assert test_type in ['impersonator', 'genuine']
    assert node_id in ['odroid4', 'rpi-8c', 'rpi-8a', 'rpi-8b', 'odroid3', 'odroid2', 'rpi-8d', 'rpi-4a', 'odroid1']


    trace_num = 6
    auth_results = []

    
        
    genuine_testing_data_by_node = testing_df.loc[testing_df['label'] == node_id]

    # Cycle through rows of genuine data from one particular node in groups of traces_for_this_run
    previous_df_chunk = 0
    for df_chunk_index in range(trace_num, len(genuine_testing_data_by_node), trace_num):
        auth_list = []
        
        single_auth_attempt = {}
        single_auth_attempt['label'] = 'genuine'

        # run rows through classification and impersonator models
        chunk_of_rows = genuine_testing_data_by_node[previous_df_chunk:df_chunk_index]
        impersonation_prediction = impersonation_detection.predict(chunk_of_rows)
        
        classification_prediction = classification.predict(chunk_of_rows)
        
        # Look at the classification results from both models, and decide if the result is match, mismatch, or impersonation.
        attempt_number = 0
        for single_impersonation_predicition, single_classification_predicition in zip(impersonation_prediction, classification_prediction):
            # print(single_impersonation_predicition)
            # print(single_classification_predicition)
            if single_impersonation_predicition == 'genuine' and single_classification_predicition == node_id:
                # print('match')
                single_auth_attempt[f'attempt_{attempt_number}'] = 'match'
            elif single_impersonation_predicition == 'genuine' and single_classification_predicition != node_id:
                # print('mismatch')
                single_auth_attempt[f'attempt_{attempt_number}'] = 'mismatch'
            else:
                # print('impersonator')
                single_auth_attempt[f'attempt_{attempt_number}'] = 'impersonator'
            attempt_number += 1
        

        auth_list.append(single_auth_attempt)
        previous_df_chunk = df_chunk_index

        auth = authenticator.predict(pd.DataFrame(auth_list))[0]
        # print(auth)

        auth_results.append(auth)
    
    print(f'Node ID: {node_id} | {test_type}')
    # print(f'Number predicted as genuine: {auth_results.count("genuine")}')
    # print(f'Number predicted as impersonator: {auth_results.count("impersonator")}')
    accuracy = (auth_results.count("genuine") - auth_results.count("impersonator")) / len(auth_results) if test_type == 'genuine' else \
        (auth_results.count("impersonator") - auth_results.count("genuine")) / len(auth_results)
    print(f'Accuracy: {round(accuracy, 2) * 100}%')



if __name__ == "__main__":
    main()

