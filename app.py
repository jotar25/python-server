
import asyncio
import datetime
import random, json
import gevent
import websockets
import time
import os
import signal
player_ids=[]
players_transform = {}
CONNECTIONS = {}
port = 7770







# register connected client to CONNECTIONS
async def register(websocket,path):
    global players_transform, player_ids,CONNECTIONS
    try:
        
        print("hello server")
        
        async for message in websocket:
            
            player_data = json.loads(message)
            
            player_id=player_data['player_id']
            CONNECTIONS[player_id]=websocket

             #print("player id = "+ player_id)
                #print("recieved : "+player_id)
            if player_data['type']=="transform":
                if player_id in players_transform:
                    #print("player exist")
                    pass 
                else:
                    print("new player connected = "+str(player_id))
                    player_ids.append(player_id)
                    ## send players list to all players
                    player_ids_list = {}
                    player_ids_list['type']='player_ids'
                    player_ids_list['player_ids']=player_ids

                    for conn in CONNECTIONS.values():
                        await conn.send(json.dumps(player_ids_list))
                players_transform[player_id]=player_data['transform']
            #################################
            if player_data['type']=="exit":
                print("player disconnected = "+str(player_id))
                CONNECTIONS.pop(player_id)
                players_transform.pop(player_id)
                player_ids.remove(player_id)
    except websockets.ConnectionClosedOK:
                print("disconnected : ")
    #except Exception as error:
        #time.sleep(3)
        #print("try again ....")



async def show_time():
    global players_transform, player_ids
    while True:
        
        message = datetime.datetime.utcnow().isoformat() + "Z"
        transforms={}
        transforms['type']='transform'
        transforms['transforms']=players_transform
        #print(players_transform)
        #print("connections = "+str(len(CONNECTIONS.keys())))
        
        for conn in CONNECTIONS.values():
            
            try:
                sent = await conn.send(json.dumps(transforms))
            except asyncio.CancelledError:
                print("disconnected : "+str(conn))
            if sent is None:
                #print("data non : "+str(sent))
                pass
            if conn.closed == True:
                pass
                
            
         
            
        #websockets.broadcast(CONNECTIONS, message)
        await asyncio.sleep(0.05)

async def main():
    async with websockets.serve(register, "", port):
        await show_time()

'''
async def main(): localhost
    # Set the stop condition when receiving SIGTERM.
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    port = int(os.environ.get("PORT", port))
    async with websockets.serve(register, "", port):
        await show_time()
        await stop
'''
if __name__ == "__main__":
    asyncio.run(main())