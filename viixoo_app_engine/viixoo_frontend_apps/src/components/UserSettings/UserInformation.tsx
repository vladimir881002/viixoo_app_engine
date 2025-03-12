import {
  Box,
  Container,
  Heading,
  Text,
} from "@chakra-ui/react"
import { useForm } from "react-hook-form"

import {
  type UserPublic
} from "@/client"
import useAuth from "@/hooks/useAuth"
import { Field } from "../ui/field"

const UserInformation = () => {
  const { user: currentUser } = useAuth()
  const {
    formState: { errors },
  } = useForm<UserPublic>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      full_name: currentUser?.full_name,
      email: currentUser?.email,
    },
  })

  return (
    <>
      <Container maxW="full">
        <Heading size="sm" py={4}>
        Información del usuario
        </Heading>
        <Box
          w={{ sm: "full", md: "sm" }}
          as="form"
        >
          <Field label="Nombre y apellidos:">
            {(
              <Text
                fontSize="md"
                py={2}
                color={!currentUser?.full_name ? "gray" : "inherit"}
                truncate
                maxW="sm"
              >
                {currentUser?.full_name || "N/A"}
              </Text>
            )}
          </Field>
          <Field
            mt={4}
            label="Email:"
            invalid={!!errors.email}
            errorText={errors.email?.message}
          >
            {(
              <Text fontSize="md" py={2} truncate maxW="sm">
                {currentUser?.email}
              </Text>
            )}
          </Field>          
        </Box>
      </Container>
    </>
  )
}

export default UserInformation
