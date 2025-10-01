from .payload import FramePayload, Hand, Landmark, NormalizedLandmark, Meta

class PayloadBuilder:
    
    @staticmethod
    def build(meta, hands) -> FramePayload:
        # Convert mediapipe results to FramePayload
        # assert meta is not None, "Meta information is required to build FramePayload."
        assert hands is not None, "Hands information is required to build FramePayload."
        
        payload = FramePayload(meta=meta, hands=[])

        hand_landmarks = hands.multi_hand_landmarks or []
        hand_world_landmarks = hands.multi_hand_world_landmarks or []
        handedness = hands.multi_handedness or []

        assert len(hand_landmarks) == len(handedness) == len(hand_world_landmarks), "Mismatch in number of detected hands."

        for i, landmarks in enumerate(hand_landmarks):
            # Get the corresponding world landmarks and handedness
            world_landmarks = hand_world_landmarks[i]
            hand_handedness = handedness[i].classification[0].label
            hand_confidence = handedness[i].classification[0].score


            landmark_list = []
            world_landmark_list = []

            # Convert each landmark to NormalizedLandmark and Landmark
            in_frame = True
            for lm in landmarks.landmark:
                if lm.x < 0 or lm.x > 1 or lm.y < 0 or lm.y > 1:
                    in_frame = False
                landmark = NormalizedLandmark(x=lm.x, y=lm.y, z=lm.z)
                landmark_list.append(landmark)

            for wlm in world_landmarks.landmark:
                world_landmark = Landmark(x=wlm.x, y=wlm.y, z=wlm.z)
                world_landmark_list.append(world_landmark)

            # Create Hand object
            hand = Hand(
                in_frame=in_frame,
                handedness=hand_handedness,
                confidence=hand_confidence,
                landmarks=landmark_list,
                world_landmarks=world_landmark_list
            )
            payload.hands.append(hand)

        return payload