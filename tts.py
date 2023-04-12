import azure.cognitiveservices.speech as speechsdk


class SpeechConverter:
    def __init__(self, subscription, region):
        self.subscription = subscription
        self.region = region
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.subscription, region=self.region)

    def text_to_speech(self, text, voice='zh-CN-XiaoxiaoNeural'):
        audio_config = speechsdk.audio.AudioOutputConfig(
            use_default_speaker=True)
        self.speech_config.speech_synthesis_voice_name = voice
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=audio_config)

        speech_synthesis_result = speech_synthesizer.speak_text_async(
            text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(
                cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(
                        cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")

    def speech_to_text(self, language='zh-CN'):
        self.speech_config.speech_recognition_language = language
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config, audio_config=audio_config)

        print("Speak into your microphone.")
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(speech_recognition_result.text))
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(
                speech_recognition_result.no_match_details))
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print("Speech Recognition canceled: {}".format(
                cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(
                    cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
        return speech_recognition_result.text