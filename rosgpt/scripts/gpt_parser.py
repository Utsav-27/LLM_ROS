#!/usr/bin/env python3


"""
This node subcribes the "user_text" topic from kai wake word node. 
Get the input from the user and send it to chatgpt to get response
"""

import rospy
from std_msgs.msg import String
from openai import OpenAI
import os
import json


openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()
print(openai_api_key)

def askGPT(text_command):
    # Create the GPT-3 prompt with example inputs and desired outputs
    prompt = '''Consider the following ontology:
                    {"action": "move", "params": {"linear_speed": linear_speed, "distance": distance, "is_forward": is_forward}}
                    {"action": "rotate", "params": {"angular_velocity": angular_velocity, "angle": angle, "is_clockwise": is_clockwise}}
                    {"action": "TurnLights", "params": {"value": value}}
                    {"action": "Email"}

                    You will be given human language prompts, and you need to return a JSON conformant to the ontology. Any action not in the ontology must be ignored. Here are some examples. 

                    prompt: "Move forward for 1 meter at a speed of 0.5 meters per second."
                    returns: {"action": "move", "params": {"linear_speed": 0.5, "distance": 1, "is_forward": true, "unit": "meter"}}

                    prompt: "Rotate 60 degree in clockwise direction at 10 degrees per second and make pizza."
                    returns: {"action": "rotate", "params": {"angular_velocity": 10, "angle": 60, "is_clockwise": true, "unit": "degrees"}}
                    
                    prompt: "Rotate 60 degrees at 20 degrees per second and then turn on the lights."
                    returns: {"action": "sequence", "params": [{"action": "rotate", "params": {"angular_velocity": 20,"angle": 60,"is_clockwise": false,"unit": degrees,}},{"action": "TurnLights","params": {"value": on}}]}

                    prompt: "Rotate 80 degrees at 10 degrees per second and then take a picture and then turn off the lights."
                    returns: {"action": "sequence", "params": [{"action": "rotate", "params": {"angular_velocity": 10,"angle": 80,"is_clockwise": false,"unit": degrees,}},{"action": "TurnLights","params": {"value": off}}]}

                    prompt: "Move the robot forward."
                    returns: {"action": "move", "params": {"linear_speed": 0.2, "distance": 1.0, "is_forward": true, "unit": "meter"}}

                    prompt: "Can you send an email?"
                    returns: {"action": "Email"}

                    prompt: "Stop the robot"
                    returns: {"action": "stop"}

                    rompt: "Stop"
                    returns: {"action": "stop"}

                    prompt: "What is the capital of India?"
                    returns: {"action": "simple_chat", params: "The capital of India is Delhi"}

                    '''
    prompt = prompt+'\nprompt: '+ str(text_command)

    try:
         response = client.chat.completions.create(
            model="gpt-3.5-turbo",
             messages=[
             {"role": "system", "content": "You are a helpful assistant"},
             {"role": "user", "content": prompt}
         ]
         )
    except Exception as e:
         rospy.logerr(f"Unexpected Error: {e}")
         return None
    chatgpt_response = response.choices[0].message.content.strip()
    if chatgpt_response is None:
        rospy.logerr("Error: Received no responce, try again!")
        return 0
    start_index = chatgpt_response.find('{')
    end_index = chatgpt_response.rfind('}') + 1
    json_response_dict = chatgpt_response[start_index:end_index]
    voice_cmd_pub.publish(json_response_dict)
    return json.dumps({'text': chatgpt_response, 'json': json_response_dict})



def parse(input:String):
    rospy.loginfo(f"The following message was received: {input}")
    rospy.loginfo("Getting GPT response")
    gpt_response_dict = askGPT(input)
    rospy.loginfo(f"Response received from ChatGPT: {str(json.loads(gpt_response_dict))}")

if __name__ == '__main__':
    rospy.init_node("gpt_parser")
    #sub = rospy.Subscriber("user_text", String, callback=parse)  # use this for kai wake word node: access voice feature
    sub = rospy.Subscriber("input_stream", String, callback=parse) # use this for client_node: access typing feature
    voice_cmd_pub = rospy.Publisher('voice_cmd', String, queue_size=10)
    rospy.loginfo('node initiated')
    
    # block until rosnode is shutdown
    rospy.spin()