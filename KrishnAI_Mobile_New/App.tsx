import React, {useState, useRef, useEffect} from 'react';
import {
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  View,
  Image,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Animated,
  Dimensions,
  Keyboard,
  Platform,
} from 'react-native';
import {getBotResponse} from './src/api/gemini';
import { StatusBar } from 'expo-status-bar';

interface Message {
  id: string;
  text: string;
  user: 'user' | 'bot';
}

export default function App() {
  const [nombre, setNombre] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);
  const sidebarAnimation = useRef(new Animated.Value(0)).current;
  const screenWidth = Dimensions.get('window').width;
  const sidebarWidth = screenWidth * 0.75;

  // Cerrar sidebar cuando se toca el teclado
  useEffect(() => {
    const keyboardDidShowListener = Keyboard.addListener(
      'keyboardDidShow',
      () => {
        if (isSidebarOpen) {
          toggleSidebar();
        }
      }
    );

    return () => {
      keyboardDidShowListener.remove();
    };
  }, [isSidebarOpen]);

  // Animar la apertura y cierre de la sidebar
  const toggleSidebar = () => {
    Animated.timing(sidebarAnimation, {
      toValue: isSidebarOpen ? 0 : 1,
      duration: 300,
      useNativeDriver: true,
    }).start();
    setSidebarOpen(!isSidebarOpen);
  };

  const sendMessage = async () => {
    if (currentMessage.trim() === '' || isLoading) {
      return;
    }

    const userMessage: Message = {
      id: Math.random().toString(),
      text: currentMessage,
      user: 'user',
    };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    // Cerrar sidebar si está abierta
    if (isSidebarOpen) {
      toggleSidebar();
    }

    try {
      // Preparar el historial de mensajes para el prompt (últimas 6 mensajes como máximo)
      const messageHistory = messages.slice(-6).map(msg => ({
        user: msg.user,
        text: msg.text
      }));

      // Pasar el historial como tercer parámetro
      const botResponseText = await getBotResponse(
        currentMessage, 
        nombre || 'Arjuna', 
        messageHistory
      );
      
      const botMessage: Message = {
        id: Math.random().toString(),
        text: botResponseText,
        user: 'bot',
      };
      setMessages(prevMessages => [...prevMessages, botMessage]);
      
      // Desplazarse hacia abajo cuando se recibe respuesta
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({animated: true});
      }, 100);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: Math.random().toString(),
        text: 'Error: No se pudo obtener respuesta.',
        user: 'bot',
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Overlay oscuro cuando el sidebar está abierto */}
      {isSidebarOpen && (
        <TouchableOpacity 
          style={styles.overlay} 
          activeOpacity={1} 
          onPress={toggleSidebar}
        />
      )}

      {/* Sidebar colapsable */}
      <Animated.View 
        style={[
          styles.sidebar,
          {
            transform: [
              { 
                translateX: sidebarAnimation.interpolate({
                  inputRange: [0, 1],
                  outputRange: [-sidebarWidth, 0],
                })
              }
            ],
            width: sidebarWidth,
          }
        ]}
      >
        <View style={styles.sidebarHeader}>
          <Image
            source={require('./assets/krishna.png')}
            style={styles.logo}
          />
          <Text style={styles.sidebarTitle}>KrishnAI</Text>
        </View>
        
        <View style={styles.sidebarContent}>
          <Text style={styles.label}>Tu nombre:</Text>
          <TextInput
            style={styles.input}
            onChangeText={setNombre}
            value={nombre}
            placeholder="Escribe tu nombre aquí"
            placeholderTextColor="#999"
          />
          
          {/* Botón para limpiar conversación */}
          <TouchableOpacity 
            style={styles.clearButton}
            onPress={() => setMessages([])}
          >
            <Text style={styles.clearButtonText}>Nueva Conversación</Text>
          </TouchableOpacity>
        </View>
      </Animated.View>

      {/* Contenido principal */}
      <View style={styles.chatArea}>
        {/* Header con botón de menú y espacio para la cámara */}
        <View style={styles.statusBarSpace} />
        <View style={styles.header}>
          <TouchableOpacity onPress={toggleSidebar} style={styles.menuButton}>
            <Text style={styles.menuIcon}>☰</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>KrishnAI</Text>
        </View>

        <ScrollView 
          style={styles.chatHistory}
          ref={scrollViewRef}
          onContentSizeChange={() => scrollViewRef.current?.scrollToEnd({animated: true})}
        >
          {messages.length === 0 && (
            <View style={styles.welcomeContainer}>
              <Image
                source={require('./assets/krishna.png')}
                style={styles.welcomeLogo}
              />
              <Text style={styles.welcomeText}>
                Bienvenido al diálogo con Krishna
              </Text>
              <Text style={styles.welcomeSubtext}>
                Haz una pregunta para comenzar tu conversación
              </Text>
            </View>
          )}
          
          {messages.map(msg => (
            <View
              key={msg.id}
              style={[
                styles.messageContainer,
                msg.user === 'user'
                  ? styles.userMessageContainer
                  : styles.botMessageContainer,
              ]}>
              {/* Icono del remitente (usando texto en lugar de imágenes) */}
              <View style={[
                styles.avatarContainer,
                msg.user === 'user' ? styles.userAvatarContainer : styles.botAvatarContainer
              ]}>
                <Text style={styles.avatarText}>
                  {msg.user === 'user' ? '👤' : 'ॐ'}
                </Text>
              </View>
              
              <View
                style={[
                  styles.messageBubble,
                  msg.user === 'user'
                    ? styles.userMessageBubble
                    : styles.botMessageBubble,
                ]}>
                <Text
                  style={[
                    styles.messageText,
                    msg.user === 'user'
                      ? styles.userMessageText
                      : styles.botMessageText,
                  ]}>
                  {msg.text}
                </Text>
              </View>
            </View>
          ))}
          {isLoading && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#666" />
            </View>
          )}
        </ScrollView>
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.messageInput}
            onChangeText={setCurrentMessage}
            value={currentMessage}
            placeholder="Escribe tu mensaje..."
            multiline
          />
          <TouchableOpacity
            style={[
              styles.sendButton,
              (!currentMessage.trim() || isLoading) && styles.disabledButton,
            ]}
            onPress={sendMessage}
            disabled={!currentMessage.trim() || isLoading}>
            <Text style={styles.sendButtonText}>↑</Text>
          </TouchableOpacity>
        </View>
      </View>
      <StatusBar style="auto" />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f7f7f8',
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    zIndex: 1,
  },
  sidebar: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: 0,
    backgroundColor: '#202123',
    zIndex: 2,
    paddingTop: Platform.OS === 'ios' ? 50 : 30,
    paddingHorizontal: 15,
  },
  sidebarHeader: {
    alignItems: 'center',
    marginBottom: 30,
    paddingTop: 20,
  },
  sidebarTitle: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 10,
  },
  sidebarContent: {
    flex: 1,
    paddingHorizontal: 10,
  },
  logo: {
    width: 80,
    height: 80,
    borderRadius: 40,
  },
  welcomeLogo: {
    width: 120,
    height: 120,
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
    color: 'white',
  },
  input: {
    width: '100%',
    height: 40,
    borderColor: '#444',
    borderWidth: 1,
    borderRadius: 5,
    paddingHorizontal: 10,
    backgroundColor: '#2d2d30',
    color: 'white',
    marginBottom: 20,
  },
  clearButton: {
    marginTop: 10,
    backgroundColor: '#555',
    borderRadius: 5,
    paddingVertical: 12,
    paddingHorizontal: 15,
    alignItems: 'center',
  },
  clearButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  statusBarSpace: {
    height: Platform.OS === 'ios' ? 45 : 25,
    backgroundColor: 'white',
  },
  header: {
    height: 60,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    backgroundColor: 'white',
  },
  menuButton: {
    padding: 10,
  },
  menuIcon: {
    fontSize: 22,
    color: '#333',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 15,
    color: '#333',
  },
  chatArea: {
    flex: 1,
  },
  chatHistory: {
    flex: 1,
    backgroundColor: '#f7f7f8',
  },
  welcomeContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 50,
    padding: 20,
  },
  welcomeText: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
    textAlign: 'center',
  },
  welcomeSubtext: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  messageContainer: {
    flexDirection: 'row',
    marginVertical: 8,
    paddingHorizontal: 10,
    alignItems: 'flex-start',
  },
  userMessageContainer: {
    justifyContent: 'flex-end',
    flexDirection: 'row-reverse',
  },
  botMessageContainer: {
    justifyContent: 'flex-start',
  },
  avatarContainer: {
    width: 36,
    height: 36,
    marginHorizontal: 8,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 18,
  },
  userAvatarContainer: {
    backgroundColor: '#666',
  },
  botAvatarContainer: {
    backgroundColor: '#e0e0e0',
  },
  avatarText: {
    fontSize: 18,
    textAlign: 'center',
  },
  messageBubble: {
    padding: 14,
    borderRadius: 10,
    maxWidth: '70%',
  },
  userMessageBubble: {
    backgroundColor: '#666', // Gris claro en vez de morado
    marginLeft: 5,
  },
  botMessageBubble: {
    backgroundColor: 'white',
    marginRight: 5,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userMessageText: {
    color: '#fff',
  },
  botMessageText: {
    color: '#333',
  },
  inputContainer: {
    flexDirection: 'row',
    paddingVertical: 10,
    paddingHorizontal: 15,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  messageInput: {
    flex: 1,
    borderColor: '#ccc',
    borderWidth: 1,
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 10,
    paddingRight: 45,
    backgroundColor: '#fff',
    maxHeight: 100,
    fontSize: 16,
  },
  sendButton: {
    backgroundColor: '#666', // Gris en vez de morado
    borderRadius: 20,
    width: 40,
    height: 40,
    position: 'absolute',
    right: 20,
    bottom: 15,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 20,
  },
  disabledButton: {
    backgroundColor: '#cccccc',
  },
  loadingContainer: {
    padding: 20,
    alignItems: 'center',
  },
});
