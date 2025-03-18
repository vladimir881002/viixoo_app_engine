import {
  Button,
  ButtonGroup,
  DialogActionTrigger,
  Text,
  VStack,
  Tabs,
  Table,
  Box,
} from "@chakra-ui/react"
import { useState } from "react"
import { GrView } from "react-icons/gr";

import type { WorkOrderPublic } from "../../client/types.gen"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"


interface WorkOrderProps {
  item: WorkOrderPublic
}

export const DetailsWorkOrders = ({ item }: WorkOrderProps) => {
  const [isOpen, setIsOpen] = useState(false) 

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button size="xs" colorPalette="gray" variant="ghost">
          <GrView fontSize="16px" />
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form>
          <DialogHeader>
            <DialogTitle>Orden de trabajo</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <VStack gap={4}>
              <Field
                label="Operación"
              >
                <Text
                  fontSize="md"
                  py={2}
                  color="inherit"
                  truncate
                  maxW="sm"
                >
                  {item?.name || ""}
                </Text>
              </Field>
              <Field
                label="Centro de trabajo"
              >
                <Text
                  fontSize="md"
                  py={2}
                  color="inherit"
                  truncate
                  maxW="sm"
                >
                  {item?.workcenter || ""}
                </Text>
              </Field>

              <Field
                label="Producto"
              >
                <Text
                  fontSize="md"
                  py={2}
                  color="inherit"
                  truncate
                  maxW="sm"
                >
                  {item?.product || ""}
                </Text>
              </Field>
              <Field
                label="Cantidad a producir"
              >
                <Text
                  fontSize="md"
                  py={2}
                  color="inherit"
                  truncate
                  maxW="sm"
                >
                  {item?.qty_remaining || ""}
                </Text>
              </Field>
              <Field
                label="Duración esperada"
              >
                <Text
                  fontSize="md"
                  py={2}
                  color="inherit"
                  truncate
                  maxW="sm"
                >
                  {item?.duration_expected || ""}
                </Text>
              </Field>
              <Field
                label="Duración real"
              >
                <Text
                  fontSize="md"
                  py={2}
                  color="inherit"
                  truncate
                  maxW="sm"
                >
                  {item?.duration || ""}
                </Text>
              </Field>
              <Field
                label="Estado"
              >
                <Text
                  fontSize="md"
                  py={2}
                  color="inherit"
                  truncate
                  maxW="sm"
                >
                  {item?.state || ""}
                </Text>
              </Field>
              <Tabs.Root defaultValue="tab-work-order-time" variant="subtle">
                <Tabs.List>
                    <Tabs.Trigger key="1" value="tab-work-order-time">
                    Seguimiento de tiempo
                    </Tabs.Trigger>
                    <Tabs.Trigger key="2" value="tab-instructions">
                    Instrucciones
                    </Tabs.Trigger>
                </Tabs.List>
               <Tabs.Content key="1" value="tab-work-order-time">
                  <Box maxH="100px" overflowY="auto" borderWidth="1px" borderRadius="md">
                    <Table.Root maxH="100px" size="sm" showColumnBorder>
                      <Table.Header>
                        <Table.Row>
                          <Table.ColumnHeader w="sm">Empleado</Table.ColumnHeader>
                          <Table.ColumnHeader w="sm">Duración</Table.ColumnHeader>
                          <Table.ColumnHeader w="sm">Inicio</Table.ColumnHeader>
                          <Table.ColumnHeader w="sm">Fin</Table.ColumnHeader>
                        </Table.Row>
                      </Table.Header>
                      <Table.Body>
                        {item.time_ids?.map((time) => (
                          <Table.Row key={time.time_id}>
                            <Table.Cell truncate maxW="sm">
                              {time.employee}
                            </Table.Cell>
                            <Table.Cell truncate maxW="sm">
                              {time.duration}
                            </Table.Cell>
                            <Table.Cell truncate maxW="30%">
                              {time.date_start}
                            </Table.Cell>
                            <Table.Cell truncate maxW="30%">
                              {time.date_end}
                            </Table.Cell>
                          </Table.Row>
                        ))}
                      </Table.Body>
                    </Table.Root>
                  </Box>
                </Tabs.Content>
                <Tabs.Content key="2" value="tab-instructions">
                    <Field
                    label="URL con las instrucciones"
                  >
                    <Text
                      fontSize="md"
                      py={2}
                      color="inherit"
                      truncate
                      maxW="sm"
                    >
                      {item?.url_document_instructions || ""}
                    </Text>
                  </Field>
                  <Field
                    label="URL de los diseños en 3D de los planos"
                  >
                    <Text
                      fontSize="md"
                      py={2}
                      color="inherit"
                      truncate
                      maxW="sm"
                    >
                      URL de los diseños en 3D de los planos:{item?.urls_plans || ""}
                    </Text>
                  </Field>
                </Tabs.Content>
              </Tabs.Root>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <ButtonGroup>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                >
                  Cerrar
                </Button>
              </DialogActionTrigger>
            </ButtonGroup>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}
