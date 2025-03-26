import {
  Box,
  Container,
  Heading,
  Input,
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
               <Input
                  id="full_name"
                  type="text"
                  defaultValue= {currentUser?.full_name || "N/A"}
                  readOnly
                >
                </Input>
            )}
          </Field>
          <Field
            mt={4}
            label="Email:"
            invalid={!!errors.email}
            errorText={errors.email?.message}
          >
            {(
              <Input
              id="email"
              type="text"
              defaultValue= {currentUser?.email || "N/A"}
              readOnly
            >
            </Input>
            )}
          </Field>
        </Box>
      </Container>
    </>
  )
}

export default UserInformation
